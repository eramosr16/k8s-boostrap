#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="${REPO_ROOT}/config.yaml"
ENV_FILE="${REPO_ROOT}/.env"

CLUSTER_DOMAIN="cluster.local"
KEYCLOAK_REALM="infra"
ROUTE_GRAFANA="grafana"
ROUTE_ARGOCD="argocd"
ROUTE_HEADLAMP="headlamp"
KEYCLOAK_URL="http://keycloak.infra.svc.cluster.local:8080"

log_info() {
    printf "[INFO] %s\n" "$1"
}

log_warn() {
    printf "[WARN] %s\n" "$1"
}

log_error() {
    printf "[ERROR] %s\n" "$1" >&2
}

require_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Required command '$1' is not installed."
        exit 1
    fi
}

load_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        return
    fi

    log_info "Loading environment overrides from $(basename "$ENV_FILE")"
    while IFS= read -r line || [ -n "$line" ]; do
        line="${line//$'\r'/}"
        line="${line%%#*}"
        if [ -z "$line" ]; then
            continue
        fi
        if ! echo "$line" | grep -Eq '^[A-Za-z_][A-Za-z0-9_]*='; then
            continue
        fi
        key="${line%%=*}"
        value="${line#*=}"
        export "$key"="$value"
    done < "$ENV_FILE"
}

load_cluster_config() {
    if [ ! -f "$CONFIG_FILE" ] || ! command -v python3 &> /dev/null; then
        return
    fi

    log_info "Loading cluster configuration from config.yaml"
    CLUSTER_DOMAIN=$(python3 - <<PY
import yaml
from pathlib import Path

path = Path("$CONFIG_FILE")
data = yaml.safe_load(path.read_text() or '') or {}
print(data.get('cluster', {}).get('domain', 'cluster.local'))
PY
)
    ROUTE_GRAFANA=$(python3 - <<PY
import yaml
from pathlib import Path

path = Path("$CONFIG_FILE")
data = yaml.safe_load(path.read_text() or '') or {}
print(data.get('routes', {}).get('grafana', 'grafana'))
PY
)
    ROUTE_ARGOCD=$(python3 - <<PY
import yaml
from pathlib import Path

path = Path("$CONFIG_FILE")
data = yaml.safe_load(path.read_text() or '') or {}
print(data.get('routes', {}).get('argocd', 'argocd'))
PY
)
    ROUTE_HEADLAMP=$(python3 - <<PY
import yaml
from pathlib import Path

path = Path("$CONFIG_FILE")
data = yaml.safe_load(path.read_text() or '') or {}
print(data.get('routes', {}).get('headlamp', 'headlamp'))
PY
)
}

require_env_var() {
    local var_name="$1"
    if [ -z "${!var_name:-}" ]; then
        log_error "Environment variable '$var_name' must be set before running this script."
        exit 1
    fi
}

get_keycloak_pod() {
    kubectl get pods -n infra -l app=keycloak -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true
}

wait_for_keycloak() {
    log_info "Waiting for Keycloak to be ready..."
    local elapsed=0
    while [ $elapsed -lt 300 ]; do
        local pod
        pod=$(get_keycloak_pod)
        if [ -n "$pod" ] && kubectl exec -n infra "$pod" -- curl -sf "$KEYCLOAK_URL/health/ready" &> /dev/null; then
            log_info "Keycloak is ready."
            return 0
        fi
        sleep 10
        elapsed=$((elapsed + 10))
    done
    log_error "Keycloak did not become ready within 5 minutes."
    exit 1
}

kc_exec() {
    local script="$1"
    local pod
    pod=$(get_keycloak_pod)
    if [ -z "$pod" ]; then
        log_error "Keycloak pod is not available."
        exit 1
    fi

    KEYCLOAK_ADMIN_PASSWORD="$KEYCLOAK_ADMIN_PASSWORD" \
        kubectl exec -n infra "$pod" -- bash -c "
            export KEYCLOAK_HOME='/opt/keycloak'
            export PATH=\"\$KEYCLOAK_HOME/bin:\$PATH\"
            set -euo pipefail
            $script
        "
}

ensure_realm() {
    log_info "Ensuring realm '$KEYCLOAK_REALM' exists..."
    kc_exec "
        REALM='$KEYCLOAK_REALM'
        kcadm config credentials --server '$KEYCLOAK_URL' --realm master --user admin --password \$KEYCLOAK_ADMIN_PASSWORD
        if kcadm get realms/\$REALM &> /dev/null; then
            echo 'Realm already exists'
        else
            kcadm create realms -s realm=\$REALM -s enabled=true -s loginWithEmailAllowed=false -s duplicateEmailsAllowed=true -s resetPasswordAllowed=false
            echo 'Realm created'
        fi
    "
}

create_client() {
    local client_id="$1"
    local params="$2"
    log_info "Ensuring Keycloak client '$client_id'..."
    kc_exec "
        REALM='$KEYCLOAK_REALM'
        kcadm config credentials --server '$KEYCLOAK_URL' --realm master --user admin --password \$KEYCLOAK_ADMIN_PASSWORD
        kcadm create clients -r '\$REALM' -s clientId=$client_id $params || true
    "
}

get_client_secret() {
    local client_id="$1"
    local secret
    secret=$(kc_exec "
        REALM='$KEYCLOAK_REALM'
        kcadm config credentials --server '$KEYCLOAK_URL' --realm master --user admin --password \$KEYCLOAK_ADMIN_PASSWORD
        CID=\$(kcadm get clients -r '\$REALM' -q clientId=$client_id --fields id 2>/dev/null | tr -d '"')
        if [ -z \"\$CID\" ]; then
            exit 0
        fi
        kcadm get clients/\$CID/client-secret -r '\$REALM' 2>/dev/null | jq -r '.value'
    "
    )
    printf "%s" "${secret//[$'\r\n']/}" # strip newlines
}

ensure_secrets() {
    local grafana_secret
    local argocd_secret
    local headlamp_secret

    grafana_secret=$(get_client_secret "$KEYCLOAK_REALM-grafana")
    argocd_secret=$(get_client_secret "$KEYCLOAK_REALM-argocd")
    headlamp_secret=$(get_client_secret "$KEYCLOAK_REALM-headlamp")

    if [ -n "$grafana_secret" ]; then
        local grafana_admin_password
        grafana_admin_password=$(kubectl get secret grafana-secret -n infra -o jsonpath='{.data.GRAFANA_ADMIN_PASSWORD}' 2>/dev/null | base64 --decode 2>/dev/null || true)

        log_info "Updating grafana-secret with refreshed client secret..."
        local grafana_cmd=(kubectl create secret generic grafana-secret -n infra)
        grafana_cmd+=(--from-literal=GRAFANA_OIDC_CLIENT_SECRET="$grafana_secret")
        if [ -n "$grafana_admin_password" ]; then
            grafana_cmd+=(--from-literal=GRAFANA_ADMIN_PASSWORD="$grafana_admin_password")
        fi
        "${grafana_cmd[@]}" --dry-run=client -o yaml | kubectl apply -f -
    else
        log_warn "Grafana client secret not available; skipping grafana-secret update."
    fi

    if [ -n "$argocd_secret" ]; then
        log_info "Updating argocd-secret with refreshed client secret..."
        kubectl create secret generic argocd-secret -n infra \
            --from-literal=OIDC_CLIENT_ID="$KEYCLOAK_REALM-argocd" \
            --from-literal=OIDC_CLIENT_SECRET="$argocd_secret" \
            --from-literal=OIDC_ISSUER_URL="$KEYCLOAK_URL/realms/$KEYCLOAK_REALM" \
            --dry-run=client -o yaml | kubectl apply -f -
    else
        log_warn "ArgoCD client secret not available; skipping argocd-secret update."
    fi

    if [ -n "$headlamp_secret" ]; then
        log_info "Updating headlamp-oidc-secret with refreshed client secret..."
        kubectl create secret generic headlamp-oidc-secret -n infra \
            --from-literal=OIDC_CLIENT_ID="${KEYCLOAK_REALM}-headlamp" \
            --from-literal=OIDC_CLIENT_SECRET="$headlamp_secret" \
            --from-literal=OIDC_ISSUER_URL="$KEYCLOAK_URL/realms/$KEYCLOAK_REALM" \
            --dry-run=client -o yaml | kubectl apply -f -
    else
        log_warn "Headlamp client secret not available; skipping headlamp-oidc-secret update."
    fi
}

main() {
    require_command kubectl
    load_env_file
    load_cluster_config
    require_env_var KEYCLOAK_ADMIN_PASSWORD

    wait_for_keycloak
    ensure_realm

    local grafana_redirects="-s 'redirectUris=[\"http://localhost:3000/*\",\"http://${ROUTE_GRAFANA}.infra.svc.cluster.local:3000/*\",\"https://${ROUTE_GRAFANA}.${CLUSTER_DOMAIN}/*\"]'"
    local grafana_params="-s clientId=${KEYCLOAK_REALM}-grafana -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true $grafana_redirects -s webOrigins='[\"+\"]' -s serviceAccountsEnabled=true"
    create_client "${KEYCLOAK_REALM}-grafana" "$grafana_params"

    local argocd_redirects="-s 'redirectUris=[\"http://localhost:8080/*\",\"http://argocd-server.argocd.svc.cluster.local:8080/*\",\"https://${ROUTE_ARGOCD}.${CLUSTER_DOMAIN}/auth/callback\"]'"
    local argocd_params="-s clientId=${KEYCLOAK_REALM}-argocd -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true $argocd_redirects -s webOrigins='[\"+\"]' -s serviceAccountsEnabled=true"
    create_client "${KEYCLOAK_REALM}-argocd" "$argocd_params"

    local headlamp_redirects="-s 'redirectUris=[\"http://localhost:4466/*\",\"http://headlamp.infra.svc.cluster.local/*\",\"https://${ROUTE_HEADLAMP}.${CLUSTER_DOMAIN}/*\"]'"
    local headlamp_params="-s clientId=${KEYCLOAK_REALM}-headlamp -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true $headlamp_redirects -s webOrigins='[\"+\"]' -s serviceAccountsEnabled=true"
    create_client "${KEYCLOAK_REALM}-headlamp" "$headlamp_params"

    ensure_secrets

    log_info "OAuth recovery completed. Grafana, ArgoCD, and Headlamp clients are refreshed."
}

main "$@"
