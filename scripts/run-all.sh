#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
HEALTH_CHECK_TIMEOUT=300
HEALTH_CHECK_INTERVAL=10
KEYCLOAK_TIMEOUT=180
CONFIG_FILE="${REPO_ROOT}/config.yaml"

CLUSTER_DOMAIN="cluster.local"
KEYCLOAK_REALM="infra"
ROUTE_ARGOCD="argocd"
ROUTE_GRAFANA="grafana"
ROUTE_HEADLAMP="headlamp"
ROUTE_KEYCLOAK="keycloak"
KEYCLOAK_HOST_IP=""
ARGOCD_CLI_VERSION="v2.9.11"
DEFAULT_DNS_FORWARDERS=("8.8.8.8" "1.1.1.1")

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

check_requirements() {
    local missing=0
    local tool
    for tool in python3 docker; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Dependency '$tool' is missing. Install it before running this script."
            missing=1
            continue
        fi
        if [ "$tool" = "docker" ]; then
            if ! docker info >/dev/null 2>&1; then
                log_warn "Docker binary is present but the daemon is unreachable. Ensure Docker is running if this script needs it."
            fi
        fi
    done
    if [ $missing -ne 0 ]; then
        exit 1
    fi
}

load_cluster_config() {
    if [ -f "$CONFIG_FILE" ]; then
        if command -v python3 &> /dev/null; then
            CLUSTER_DOMAIN=$(python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    d = yaml.safe_load(f)
    print(d.get('cluster', {}).get('domain', 'cluster.local'))
" 2>/dev/null) || CLUSTER_DOMAIN="cluster.local"
            KEYCLOAK_REALM=$(python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    d = yaml.safe_load(f)
    print(d.get('keycloak', {}).get('realm', 'infra'))
" 2>/dev/null) || KEYCLOAK_REALM="infra"
            ROUTE_ARGOCD=$(python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    d = yaml.safe_load(f)
    print(d.get('routes', {}).get('argocd', 'argocd'))
" 2>/dev/null) || ROUTE_ARGOCD="argocd"
            ROUTE_GRAFANA=$(python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    d = yaml.safe_load(f)
    print(d.get('routes', {}).get('grafana', 'grafana'))
" 2>/dev/null) || ROUTE_GRAFANA="grafana"
            ROUTE_HEADLAMP=$(python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    d = yaml.safe_load(f)
    print(d.get('routes', {}).get('headlamp', 'headlamp'))
" 2>/dev/null) || ROUTE_HEADLAMP="headlamp"
            ROUTE_KEYCLOAK=$(python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    d = yaml.safe_load(f)
    print(d.get('routes', {}).get('keycloak', 'keycloak'))
" 2>/dev/null) || ROUTE_KEYCLOAK="keycloak"
            KEYCLOAK_HOST_IP=$(python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    d = yaml.safe_load(f)
    print(d.get('cluster', {}).get('hostIP', ''))
" 2>/dev/null) || KEYCLOAK_HOST_IP=""
            TRAEFIK_EMAIL=$(python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    d = yaml.safe_load(f)
    print(d.get('traefik', {}).get('email', ''))
" 2>/dev/null) || TRAEFIK_EMAIL=""
        fi
    fi
    export CLUSTER_DOMAIN KEYCLOAK_REALM
    export ROUTE_ARGOCD ROUTE_GRAFANA ROUTE_HEADLAMP ROUTE_KEYCLOAK
    export KEYCLOAK_HOST_IP TRAEFIK_EMAIL
}

check_requirements
load_cluster_config

require_config_update() {
    if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        log_warn "Unable to validate git status for ${CONFIG_FILE}; ensure it's customized before running."
        return 0
    fi

    local status_line
    status_line=$(git -C "$REPO_ROOT" status --short -- "config.yaml" 2>/dev/null)
    if [ -z "$status_line" ]; then
        log_error "${CONFIG_FILE} has not changed. Please edit it with your cluster values before running this script."
        exit 1
    fi
}

require_config_update

check_dns_forwarders() {
    if ! command -v nslookup &> /dev/null; then
        log_warn "nslookup is unavailable; skipping DNS forwarder reachability check."
        return
    fi

    local resolver
    local failed=0

    for resolver in "${DEFAULT_DNS_FORWARDERS[@]}"; do
        if nslookup github.com "$resolver" >/dev/null 2>&1; then
            log_info "DNS forwarder $resolver can resolve github.com."
        else
            log_warn "DNS forwarder $resolver cannot reach github.com."
            failed=1
        fi
    done

    if [ "$failed" -ne 0 ]; then
        log_warn "Verify connectivity to the DNS forwarders above if CoreDNS still cannot reach external names."
    fi
}

create_keycloak_infra_realm() {
    log_info "=== Creating Keycloak infra Realm ==="
    
    local keycloak_pod
    keycloak_pod=$(kubectl get pods -n infra -l app=keycloak -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -z "$keycloak_pod" ]; then
        log_error "Keycloak pod not found"
        return 1
    fi
    
    export KEYCLOAK_HOME="/opt/keycloak"
    export PATH="$KEYCLOAK_HOME/bin:$PATH"
    
    local keycloak_url="http://keycloak.infra.svc.cluster.local:8080"
    local keycloak_external="https://keycloak.${CLUSTER_DOMAIN:-cluster.local}"
    
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
        for i in {1..30}; do
            if kubectl exec -n infra "$keycloak_pod" -- curl -sf "$keycloak_url/realms/master" &> /dev/null; then
                api_ready=true
                break
            fi
            sleep 2
        done
    fi
    
    log_info "Creating $KEYCLOAK_REALM realm..."
    
    kubectl exec -n infra "$keycloak_pod" -- bash -c "
        export KEYCLOAK_HOME='/opt/keycloak'
        export PATH=\"\$KEYCLOAK_HOME/bin:\$PATH\"
        REALM='$KEYCLOAK_REALM'
        
        kcadm config credentials --server '$keycloak_url' --realm master --user admin --password '\$KEYCLOAK_ADMIN_PASSWORD' || exit 1
        
        if kcadm get realms/\$REALM &> /dev/null; then
            echo \"\$REALM realm already exists\"
        else
            kcadm create realms -s realm=\$REALM -s enabled=true -s loginWithEmailAllowed=false -s duplicateEmailsAllowed=true -s resetPasswordAllowed=false
            echo \"\$REALM realm created\"
        fi
    "
    
    log_info "Creating $KEYCLOAK_REALM realm clients..."
    
    local grafana_uri="https://${ROUTE_GRAFANA}.${CLUSTER_DOMAIN}"
    local argocd_uri="https://${ROUTE_ARGOCD}.${CLUSTER_DOMAIN}"
    local headlamp_uri="https://${ROUTE_HEADLAMP}.${CLUSTER_DOMAIN}"
    local headlamp_uri="https://${ROUTE_HEADLAMP}.${CLUSTER_DOMAIN}"
    
    kubectl exec -n infra "$keycloak_pod" -- bash -c "
        export KEYCLOAK_HOME='/opt/keycloak'
        export PATH=\"\$KEYCLOAK_HOME/bin:\$PATH\"
        REALM='$KEYCLOAK_REALM'
        
        kcadm config credentials --server '$keycloak_url' --realm master --user admin --password '\$KEYCLOAK_ADMIN_PASSWORD' || exit 1
        
        echo 'Creating k3s-api client...'
        kcadm create clients -r '\$REALM' -s clientId=k3s-api -s enabled=true -s protocol=openid-connect -s publicClient=false -s serviceAccountsEnabled=true -s standardFlowEnabled=false -s directAccessGrantsEnabled=true
        
        echo 'Creating Grafana client...'
        kcadm create clients -r '\$REALM' -s clientId=\$REALM-grafana -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s 'redirectUris=[\"http://localhost:3000/*\",\"http://grafana.infra.svc.cluster.local:3000/*\"]' -s webOrigins='[\"+\"]' -s serviceAccountsEnabled=true || true
        
        echo 'Creating ArgoCD client...'
        kcadm create clients -r '\$REALM' -s clientId=\$REALM-argocd -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s 'redirectUris=[\"http://localhost:8080/*\",\"http://argocd-server.argocd.svc.cluster.local:8080/*\"]' -s webOrigins='[\"+\"]' -s serviceAccountsEnabled=true || true
        
        echo 'Creating Headlamp client...'
        kcadm create clients -r '\$REALM' -s clientId=\$REALM-headlamp -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s 'redirectUris=[\"http://localhost:4466/*\",\"http://headlamp.infra.svc.cluster.local/*\"]' -s webOrigins='[\"+\"]' -s serviceAccountsEnabled=true || true
        
        echo \"\$REALM clients created\"
    "
    
    log_info " $KEYCLOAK_REALM realm setup complete."
}

configure_k3s_oidc() {
    log_info "=== Configuring K3s OIDC with Keycloak ==="
    
    local keycloak_external="https://keycloak.${CLUSTER_DOMAIN:-cluster.local}"
    local k3s_config_dir="/etc/rancher/k3s"
    
    mkdir -p "$k3s_config_dir"
    
    cat > "${k3s_config_dir}/k3s_server.yaml" << EOFCONFIG
kube-apiserver-arg:
  - oidc-issuer-url=https://keycloak.cluster.local/realms/$KEYCLOAK_REALM
  - oidc-username-claim=preferred_username
  - oidc-groups-claim=groups
  - oidc-client-id=k3s-api
EOFCONFIG
    
    sed -i "s/keycloak.cluster.local/${CLUSTER_DOMAIN:-cluster.local}/g" "${k3s_config_dir}/k3s_server.yaml"
    
    log_info "K3s OIDC config written to ${k3s_config_dir}/k3s_server.yaml"
    log_info "Restart K3s to apply: sudo systemctl restart k3s"
}

prompt_secret() {
    local name="$1"
    local var_name="$2"
    local description="$3"
    local allow_empty="$4"
    local value=""
    local prefilled="${!var_name}"

    if [ -n "$prefilled" ]; then
        echo "$prefilled"
        return 0
    fi

    log_warn "Environment variable '$var_name' is not set; prompting for '$name'."
    local prompt_message="$description [$var_name]: "

    while true; do
        if ! read -s -r -p "$prompt_message" value; then
            log_error "Failed to read $name"
            return 1
        fi
        printf "\n" >&2

        if [ -z "$value" ]; then
            if [ "$allow_empty" = "true" ]; then
                echo ""
                return 0
            fi
            log_error "$name cannot be empty. Please try again."
            continue
        fi

        echo "$value"
        return 0
    done
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

prompt_confirmation() {
    local prompt="$1"
    if [ ! -t 0 ]; then
        log_warn "Non-interactive shell detected; defaulting to 'no'."
        return 1
    fi

    while true; do
        read -rp "$prompt [y/N]: " response
        case "${response,,}" in
            y|yes)
                return 0
                ;;
            n|no|"")
                return 1
                ;;
            *)
                echo "Please answer yes or no.";
                ;;
        esac
    done
}

reset_existing_argocd() {
    if ! kubectl get namespace argocd &> /dev/null; then
        return 0
    fi

    log_warn "An existing ArgoCD installation was detected."
    if ! prompt_confirmation "Delete the current ArgoCD namespace and all cached applications so we can start fresh?"; then
        log_info "Keeping existing ArgoCD installation as requested."
        return 0
    fi

    log_info "Deleting namespace argocd to clear previous ArgoCD resources..."
    kubectl delete namespace argocd --ignore-not-found
    while kubectl get namespace argocd &> /dev/null; do
        sleep 2
    done
    log_info "ArgoCD namespace removed. A fresh installation will be applied next."
}

install_argocd() {
    log_info "Installing ArgoCD..."

    if ! kubectl get namespace argocd &> /dev/null; then
        kubectl create namespace argocd
    fi

    log_info "Removing any existing argocd-server service before installing upstream manifests..."
    kubectl delete svc argocd-server -n argocd --ignore-not-found
    kubectl apply --server-side --force-conflicts -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    log_info "Re-applying the custom 8080-only argocd-server service..."
    kubectl delete svc argocd-server -n argocd --ignore-not-found
    kubectl apply -n argocd -f infra/services/observability/argocd/argocd-server-service.yaml

    log_info "Waiting for ArgoCD to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

    log_info "ArgoCD installed successfully."
}

install_argocd_cli() {
    log_info "Ensuring ArgoCD CLI is installed..."

    if command -v argocd &> /dev/null; then
        log_info "argocd CLI already available at $(command -v argocd)"
        return 0
    fi

    local version="${ARGOCD_CLI_VERSION}"
    local os="linux"
    local arch="$(uname -m)"
    case "$arch" in
        x86_64) arch="amd64" ;; 
        aarch64|arm64) arch="arm64" ;;
        *) arch="${arch}" ;;
    esac

    local download_url="https://github.com/argoproj/argo-cd/releases/download/${version}/argocd-${os}-${arch}"
    local tmpfile
    tmpfile=$(mktemp)

    local attempt
    for attempt in 1 2 3; do
        if curl -fsSL -o "$tmpfile" "$download_url"; then
            break
        fi
        log_warn "Attempt $attempt failed to download argocd CLI, retrying..."
        sleep 1
    done

    if [ ! -s "$tmpfile" ]; then
        log_error "Failed to download argocd CLI from $download_url"
        rm -f "$tmpfile"
        exit 1
    fi

    chmod +x "$tmpfile"
    local target="/usr/local/bin/argocd"
    if [ -w "$(dirname "$target")" ]; then
        mv "$tmpfile" "$target"
    else
        sudo mv "$tmpfile" "$target"
    fi

    log_info "argocd CLI installed at $target"
}

readonly CREDENTIAL_PROMPTS=(
    "PostgreSQL Password|POSTGRES_PASSWORD|Enter PostgreSQL password|false"
    "Redis Password|REDIS_PASSWORD|Enter Redis password|false"
    "RabbitMQ Username|RABBITMQ_DEFAULT_USER|Enter RabbitMQ username|false"
    "RabbitMQ Password|RABBITMQ_DEFAULT_PASS|Enter RabbitMQ password|false"
    "Keycloak Admin Password|KEYCLOAK_ADMIN_PASSWORD|Enter Keycloak admin password|false"
    "Keycloak Database Password|KEYCLOAK_DATABASE_PASSWORD|Enter Keycloak database password|false"
    "Let's Encrypt Email|LETS_ENCRYPT_EMAIL|Enter Let's Encrypt email for Traefik ACME|false"
    "AWS Access Key ID|AWS_ACCESS_KEY_ID|Enter AWS access key (or press Enter to skip)|true"
    "AWS Secret Access Key|AWS_SECRET_ACCESS_KEY|Enter AWS secret key (or press Enter to skip)|true"
)

prompt_secrets() {
    log_info "=== Credential Setup ==="
    log_info "Please enter credentials for all services."
    echo
    local definition
    for definition in "${CREDENTIAL_PROMPTS[@]}"; do
        IFS='|' read -r name env_var prompt allow_empty <<< "$definition"
        allow_empty=${allow_empty:-false}
        local value
        if ! value=$(prompt_secret "$name" "$env_var" "$prompt" "$allow_empty"); then
            exit 1
        fi
        export "$env_var=$value"
    done

    log_info "Credentials collected."

    if [ -z "$TRAEFIK_EMAIL" ] && [ -n "$LETS_ENCRYPT_EMAIL" ]; then
        TRAEFIK_EMAIL="$LETS_ENCRYPT_EMAIL"
        export TRAEFIK_EMAIL
    fi
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
        --from-literal=RABBITMQ_DEFAULT_USER="$RABBITMQ_DEFAULT_USER" \
        --from-literal=RABBITMQ_DEFAULT_PASS="$RABBITMQ_DEFAULT_PASS" \
        --dry-run=client -o yaml | kubectl apply -f -

    kubectl create secret generic keycloak-secret -n infra \
        --from-literal=KEYCLOAK_ADMIN_PASSWORD="$KEYCLOAK_ADMIN_PASSWORD" \
        --from-literal=KEYCLOAK_DATABASE_PASSWORD="$KEYCLOAK_DATABASE_PASSWORD" \
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
    log_info "Applying root-app.yaml to trigger ArgoCD sync (images are defined in the ArgoCD manifests and not rewritten here)..."
    
    ROOT_APP="${REPO_ROOT}/boostrap/root-app.yaml"
    
    if [ ! -f "$ROOT_APP" ]; then
        log_error "root-app.yaml not found at $ROOT_APP"
        exit 1
    fi
    
    kubectl apply -f "$ROOT_APP"
    patch_traefik_templates
    log_info "Root Application applied."
}

render_template() {
    local template="$1"
    python3 - "$template" <<'PY'
import os
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text()

def substitute(match):
    key = match.group(1)
    return os.environ.get(key, match.group(0))

print(re.sub(r"\{\{([A-Z0-9_]+)\}\}", substitute, text))
PY
}

patch_traefik_templates() {
    if [ -z "$TRAEFIK_EMAIL" ]; then
        log_warn "TRAEFIK_EMAIL not configured; skipping Traefik template rendering."
        return 0
    fi

    local template_dir="${REPO_ROOT}/infra/services/gateway"
    log_info "Applying user-specific Traefik configuration from config.yaml..."
    render_template "$template_dir/traefik-config.yaml" | kubectl apply -f -
    render_template "$template_dir/traefik-acme-secret.yaml" | kubectl apply -f -
    log_info "Traefik email from config.yaml applied to kube-system resources."
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
            -s 'redirectUris=[\"http://localhost:8080/*\",\"http://argocd-server.argocd.svc.cluster.local:8080/*\"]' \
            -s webOrigins='[\"+\"]' \
            -s serviceAccountsEnabled=true
        
        echo 'Creating Headlamp client...'
        kcadm create clients -r '$realm' \
            -s clientId=headlamp \
            -s enabled=true \
            -s protocol=openid-connect \
            -s publicClient=false \
            -s standardFlowEnabled=true \
            -s 'redirectUris=[\"http://localhost:4466/*\",\"http://headlamp.infra.svc.cluster.local/*\"]' \
            -s webOrigins='[\"+\"]' \
            -s serviceAccountsEnabled=true
        "
    
    log_info "Retrieving client secrets from Keycloak..."
    
    local grafana_secret argocd_secret headlamp_secret
    
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
    
    headlamp_secret=$(kubectl exec -n infra "$keycloak_pod" -- bash -c "
        export KEYCLOAK_HOME='/opt/keycloak'
        export PATH=\"\$KEYCLOAK_HOME/bin:\$PATH\"
        
        CID=\$(kcadm get clients -r master -q clientId=headlamp --fields id 2>/dev/null | tr -d '\"')
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
    
    if [ -n "$headlamp_secret" ] && [ "$headlamp_secret" != "null" ]; then
        kubectl create secret generic headlamp-oidc-secret -n infra \
            --from-literal=OIDC_CLIENT_ID=headlamp \
            --from-literal=OIDC_CLIENT_SECRET="$headlamp_secret" \
            --from-literal=OIDC_ISSUER_URL="$keycloak_url/realms/master" \
            --dry-run=client -o yaml | kubectl apply -f -
        log_info "Headlamp OIDC secret created with Keycloak credentials."
    else
        log_warn "Could not retrieve Headlamp client secret."
    fi
    
    log_info "Keycloak clients configured."
    ensure_keycloak_dns_alias
}

ensure_keycloak_dns_alias() {
    local alias_domain="auth.${CLUSTER_DOMAIN:-cluster.local}"
    local alias_line="$KEYCLOAK_HOST_IP $alias_domain"
    local nodehosts="/etc/coredns/NodeHosts"

    if [ -z "$KEYCLOAK_HOST_IP" ]; then
        log_error "cluster.hostIP is not configured in $CONFIG_FILE. Set the alias IP before touching CoreDNS hosts."
        exit 1
    fi

    if [ ! -f "$nodehosts" ]; then
        log_warn "$nodehosts not found; creating placeholder file."
        sudo touch "$nodehosts" || true
    fi

    if sudo grep -Fxq "$alias_line" "$nodehosts" 2>/dev/null; then
        log_info "Keycloak auth alias already present in $nodehosts."
    else
        log_info "Adding Keycloak auth alias to $nodehosts."
        echo "$alias_line" | sudo tee -a "$nodehosts" >/dev/null
    fi

    log_info "Restarting CoreDNS so it picks up the alias."
    if kubectl -n kube-system rollout restart deployment/coredns >/dev/null 2>&1; then
        log_info "CoreDNS restart triggered."
    else
        log_warn "CoreDNS restart failed; check kubeconfig/permissions."
    fi

    check_dns_forwarders
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

    reset_existing_argocd
    install_argocd
    install_argocd_cli
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
    
    create_keycloak_infra_realm
    echo
    
    configure_k3s_oidc
    echo
    
    prompt_grafana_password
    echo
    
    configure_keycloak_clients
    echo

    if poll_applications; then
        log_info "=== Bootstrap Complete ==="
        log_info "All services are healthy!"
        log_info "ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:8080"
        log_info "Keycloak: kubectl port-forward svc/keycloak -n infra 8080:8080"
        log_info "Headlamp: kubectl port-forward svc/headlamp -n infra 4466:80"
        log_info "  (Login with: kubectl create token headlamp -n infra)"
        exit 0
    else
        log_error "=== Bootstrap Failed ==="
        log_error "Some services did not become healthy within timeout."
        exit 1
    fi
}

main "$@"
