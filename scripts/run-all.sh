#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
HEALTH_CHECK_TIMEOUT=300
HEALTH_CHECK_INTERVAL=10
KEYCLOAK_TIMEOUT=180

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

prompt_secret() {
    local name="$1"
    local var_name="$2"
    local description="$3"
    local allow_empty="$4"
    local value=""
    
    while [ -z "$value" ]; do
        echo -n "$description [$var_name]: "
        read -s value
        echo
        if [ -z "$value" ]; then
            if [ "$allow_empty" = "true" ]; then
                return 0
            fi
            log_error "$name cannot be empty. Please try again."
        fi
    done
    echo "$value"
}

install_k3s() {
    log_info "Checking for K3s..."
    
    if command -v k3s &> /dev/null; then
        log_info "K3s is already installed: $(k3s --version)"
        if systemctl is-active --quiet k3s; then
            log_info "K3s service is running."
        else
            log_warn "K3s is installed but not running. Starting service..."
            sudo systemctl start k3s
        fi
    else
        log_info "K3s not found. Installing K3s..."
        curl -sfL https://get.k3s.io | sh -
        log_info "K3s installed successfully."
    fi
    
    log_info "Setting up kubectl configuration..."
    K3S_KUBECONFIG="/etc/rancher/k3s/k3s.yaml"
    KUBECONFIG_DIR="${HOME}/.kube"
    KUBECONFIG_FILE="${KUBECONFIG_DIR}/config"
    
    mkdir -p "${KUBECONFIG_DIR}"
    
    if [ -f "${K3S_KUBECONFIG}" ]; then
        if [ ! -f "${KUBECONFIG_FILE}" ] || ! diff -q "${K3S_KUBECONFIG}" "${KUBECONFIG_FILE}" &> /dev/null; then
            sudo cp "${K3S_KUBECONFIG}" "${KUBECONFIG_FILE}"
            sudo chmod 600 "${KUBECONFIG_FILE}"
            log_info "Kubeconfig copied to ${KUBECONFIG_FILE}"
        else
            log_info "Kubeconfig already configured."
        fi
    fi
    
    export KUBECONFIG="${KUBECONFIG_FILE}"
    log_info "Verifying cluster connectivity..."
    kubectl cluster-info
    log_info "K3s setup complete."
}

install_argocd() {
    log_info "Installing ArgoCD..."
    
    if ! kubectl get namespace argocd &> /dev/null; then
        kubectl create namespace argocd
    fi
    
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    
    log_info "Waiting for ArgoCD to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s
    
    log_info "ArgoCD installed successfully."
}

prompt_secrets() {
    log_info "=== Credential Setup ==="
    log_info "Please enter credentials for all services."
    echo
    
    POSTGRES_PASSWORD=$(prompt_secret "PostgreSQL Password" "POSTGRES_PASSWORD" "Enter PostgreSQL password")
    REDIS_PASSWORD=$(prompt_secret "Redis Password" "REDIS_PASSWORD" "Enter Redis password")
    RABBITMQ_USER=$(prompt_secret "RabbitMQ User" "RABBITMQ_DEFAULT_USER" "Enter RabbitMQ username")
    RABBITMQ_PASS=$(prompt_secret "RabbitMQ Password" "RABBITMQ_DEFAULT_PASS" "Enter RabbitMQ password")
    KEYCLOAK_ADMIN_PASSWORD=$(prompt_secret "Keycloak Admin Password" "KEYCLOAK_ADMIN_PASSWORD" "Enter Keycloak admin password")
    KEYCLOAK_DB_PASSWORD=$(prompt_secret "Keycloak Database Password" "KEYCLOAK_DATABASE_PASSWORD" "Enter Keycloak database password")
    SEQ_ADMIN_PASSWORD=$(prompt_secret "Seq Admin Password" "SEQ_ADMIN_PASSWORD" "Enter Seq admin password")
    LETS_ENCRYPT_EMAIL=$(prompt_secret "Let's Encrypt Email" "LETS_ENCRYPT_EMAIL" "Enter Let's Encrypt email for Traefik ACME")
    AWS_ACCESS_KEY_ID=$(prompt_secret "AWS Access Key ID" "AWS_ACCESS_KEY_ID" "Enter AWS access key (or press Enter to skip)" "true")
    AWS_SECRET_ACCESS_KEY=$(prompt_secret "AWS Secret Access Key" "AWS_SECRET_ACCESS_KEY" "Enter AWS secret key (or press Enter to skip)" "true")
    
    export POSTGRES_PASSWORD REDIS_PASSWORD RABBITMQ_USER RABBITMQ_PASS
    export KEYCLOAK_ADMIN_PASSWORD KEYCLOAK_DB_PASSWORD
    export SEQ_ADMIN_PASSWORD LETS_ENCRYPT_EMAIL
    export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
    
    log_info "Credentials collected."
}

create_secrets() {
    log_info "Creating Kubernetes secrets..."
    
    kubectl create namespace infra --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic postgres-secret -n infra \
        --from-literal=password="$POSTGRES_PASSWORD" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic redis-secret -n infra \
        --from-literal=password="$REDIS_PASSWORD" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic rabbitmq-secret -n infra \
        --from-literal=username="$RABBITMQ_USER" \
        --from-literal=password="$RABBITMQ_PASS" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic keycloak-secret -n infra \
        --from-literal=admin-password="$KEYCLOAK_ADMIN_PASSWORD" \
        --from-literal=database-password="$KEYCLOAK_DB_PASSWORD" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic seq-secret -n infra \
        --from-literal=admin-password="$SEQ_ADMIN_PASSWORD" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    kubectl create secret generic traefik-acme-secret -n infra \
        --from-literal=email="$LETS_ENCRYPT_EMAIL" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        kubectl create secret generic aws-ecr-secret -n infra \
            --from-literal=aws-access-key-id="$AWS_ACCESS_KEY_ID" \
            --from-literal=aws-secret-access-key="$AWS_SECRET_ACCESS_KEY" \
            --dry-run=client -o yaml | kubectl apply -f -
    fi
    
    log_info "Secrets created."
}

apply_root_app() {
    log_info "Applying root-app.yaml to trigger ArgoCD sync..."
    
    ROOT_APP="${REPO_ROOT}/boostrap/root-app.yaml"
    
    if [ ! -f "$ROOT_APP" ]; then
        log_error "root-app.yaml not found at $ROOT_APP"
        exit 1
    fi
    
    kubectl apply -f "$ROOT_APP"
    log_info "Root Application applied."
}

wait_for_keycloak() {
    log_info "Waiting for Keycloak to be ready..."
    
    local elapsed=0
    while [ $elapsed -lt $KEYCLOAK_TIMEOUT ]; do
        local keycloak_ready=$(kubectl get pods -n infra -l app=keycloak -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "")
        
        if [ "$keycloak_ready" = "True" ]; then
            log_info "Keycloak is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 10
        elapsed=$((elapsed + 10))
    done
    
    echo
    log_error "Timeout waiting for Keycloak to be ready."
    return 1
}

get_keycloak_pod() {
    kubectl get pods -n infra -l app=keycloak -o jsonpath='{.items[0].metadata.name}' 2>/dev/null
}

configure_keycloak_clients() {
    log_info "=== Configuring Keycloak Clients ==="
    
    local keycloak_pod
    keycloak_pod=$(get_keycloak_pod)
    
    if [ -z "$keycloak_pod" ]; then
        log_error "Keycloak pod not found"
        return 1
    fi
    
    export KEYCLOAK_HOME="/opt/keycloak"
    export PATH="$KEYCLOAK_HOME/bin:$PATH"
    
    local keycloak_url="http://keycloak.infra.svc.cluster.local:8080"
    local realm="master"
    
    log_info "Waiting for Keycloak API to be ready..."
    local api_ready=false
    for i in {1..30}; do
        if kubectl exec -n infra "$keycloak_pod" -- curl -sf "$keycloak_url/health/ready" &> /dev/null; then
            api_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$api_ready" = "false" ]; then
        log_warn "Keycloak API not ready yet, using alternative endpoint check..."
        for i in {1..30}; do
            if kubectl exec -n infra "$keycloak_pod" -- curl -sf "$keycloak_url/realms/master" &> /dev/null; then
                api_ready=true
                break
            fi
            sleep 2
        done
    fi
    
    log_info "Creating Keycloak clients using kcadm..."
    
    kubectl exec -n infra "$keycloak_pod" -- bash -c "
        export KEYCLOAK_HOME='/opt/keycloak'
        export PATH=\"\$KEYCLOAK_HOME/bin:\$PATH\"
        
        kcadm config credentials \
            --server '$keycloak_url' \
            --realm '$realm' \
            --user admin \
            --password '$KEYCLOAK_ADMIN_PASSWORD'
        
        echo 'Creating Grafana client...'
        kcadm create clients -r '$realm' \
            -s clientId=grafana \
            -s enabled=true \
            -s protocol=openid-connect \
            -s publicClient=false \
            -s standardFlowEnabled=true \
            -s 'redirectUris=[\"http://localhost:3000/*\",\"http://grafana.infra.svc.cluster.local:3000/*\"]' \
            -s webOrigins='[\"+\"]' \
            -s serviceAccountsEnabled=true
        
        echo 'Creating ArgoCD client...'
        kcadm create clients -r '$realm' \
            -s clientId=argocd \
            -s enabled=true \
            -s protocol=openid-connect \
            -s publicClient=false \
            -s standardFlowEnabled=true \
            -s 'redirectUris=[\"http://localhost:8080/*\",\"http://argocd.infra.svc.cluster.local/*\"]' \
            -s webOrigins='[\"+\"]' \
            -s serviceAccountsEnabled=true
        
        echo 'Clients created successfully.'
    "
    
    log_info "Retrieving client secrets from Keycloak..."
    
    local grafana_secret argocd_secret
    
    grafana_secret=$(kubectl exec -n infra "$keycloak_pod" -- bash -c "
        export KEYCLOAK_HOME='/opt/keycloak'
        export PATH=\"\$KEYCLOAK_HOME/bin:\$PATH\"
        
        CID=\$(kcadm get clients -r master -q clientId=grafana --fields id 2>/dev/null | tr -d '\"')
        if [ -n \"\$CID\" ]; then
            kcadm get clients/\$CID/client-secret -r master 2>/dev/null | jq -r '.value' 2>/dev/null || echo ''
        fi
    " | tr -d '\r\n')
    
    argocd_secret=$(kubectl exec -n infra "$keycloak_pod" -- bash -c "
        export KEYCLOAK_HOME='/opt/keycloak'
        export PATH=\"\$KEYCLOAK_HOME/bin:\$PATH\"
        
        CID=\$(kcadm get clients -r master -q clientId=argocd --fields id 2>/dev/null | tr -d '\"')
        if [ -n \"\$CID\" ]; then
            kcadm get clients/\$CID/client-secret -r master 2>/dev/null | jq -r '.value' 2>/dev/null || echo ''
        fi
    " | tr -d '\r\n')
    
    log_info "Updating Grafana and ArgoCD secrets with client credentials..."
    
    if [ -n "$grafana_secret" ] && [ "$grafana_secret" != "null" ]; then
        kubectl create secret generic grafana-secret -n infra \
            --from-literal=admin-password="$GRAFANA_ADMIN_PASSWORD" \
            --from-literal=oidc-client-secret="$grafana_secret" \
            --dry-run=client -o yaml | kubectl apply -f -
        log_info "Grafana secret updated with Keycloak client secret."
    else
        log_warn "Could not retrieve Grafana client secret. Using manual input."
        if [ -n "$GRAFANA_ADMIN_PASSWORD" ]; then
            kubectl create secret generic grafana-secret -n infra \
                --from-literal=admin-password="$GRAFANA_ADMIN_PASSWORD" \
                --from-literal=oidc-client-secret="$GRAFANA_CLIENT_SECRET" \
                --dry-run=client -o yaml | kubectl apply -f -
        fi
    fi
    
    if [ -n "$argocd_secret" ] && [ "$argocd_secret" != "null" ]; then
        log_info "ArgoCD client secret retrieved."
    else
        log_warn "Could not retrieve ArgoCD client secret."
    fi
    
    log_info "Keycloak clients configured."
}

prompt_grafana_password() {
    GRAFANA_ADMIN_PASSWORD=$(prompt_secret "Grafana Admin Password" "GRAFANA_ADMIN_PASSWORD" "Enter Grafana admin password")
    export GRAFANA_ADMIN_PASSWORD
}

poll_applications() {
    log_info "Polling for application health..."
    
    local elapsed=0
    while [ $elapsed -lt $HEALTH_CHECK_TIMEOUT ]; do
        local unhealthy=$(kubectl get applications -n argocd -o jsonpath='{range .items[?(@.status.health.status!="Healthy")]} {.metadata.name}{"\n"}{end}' 2>/dev/null || echo "")
        
        if [ -z "$unhealthy" ]; then
            local all_apps=$(kubectl get applications -n argocd -o name 2>/dev/null | wc -l)
            if [ "$all_apps" -gt 0 ]; then
                log_info "All applications are healthy!"
                return 0
            fi
        fi
        
        echo -n "."
        sleep $HEALTH_CHECK_INTERVAL
        elapsed=$((elapsed + HEALTH_CHECK_INTERVAL))
    done
    
    echo
    log_error "Timeout waiting for applications to become healthy."
    
    log_warn "Current application status:"
    kubectl get applications -n argocd 2>/dev/null || true
    
    return 1
}

main() {
    log_info "=== K8s Cluster Bootstrap Script ==="
    log_info "This script will install K3s, ArgoCD, create secrets, configure Keycloak, and verify service health."
    echo
    
    install_k3s
    echo
    
    install_argocd
    echo
    
    prompt_secrets
    echo
    
    create_secrets
    echo
    
    apply_root_app
    echo
    
    log_info "Waiting for base services (PostgreSQL, Redis, Keycloak) to be ready..."
    sleep 30
    
    wait_for_keycloak
    echo
    
    prompt_grafana_password
    echo
    
    configure_keycloak_clients
    echo
    
    if poll_applications; then
        log_info "=== Bootstrap Complete ==="
        log_info "All services are healthy!"
        log_info "ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
        log_info "Keycloak: kubectl port-forward svc/keycloak -n infra 8080:8080"
        exit 0
    else
        log_error "=== Bootstrap Failed ==="
        log_error "Some services did not become healthy within timeout."
        exit 1
    fi
}

main "$@"
