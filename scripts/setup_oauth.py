#!/usr/bin/env python3
"""Setup OAuth with Keycloak for Grafana, ArgoCD, and Headlamp."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = REPO_ROOT / "config.yaml"
ENV_FILE = REPO_ROOT / ".env"

CLUSTER_DOMAIN = "cluster.local"
KEYCLOAK_REALM = "infra"
ROUTE_GRAFANA = "grafana"
ROUTE_ARGOCD = "argocd"
ROUTE_HEADLAMP = "headlamp"
KEYCLOAK_URL = "http://keycloak.infra.svc.cluster.local:8080"


def log_info(msg: str):
    print(f"[INFO] {msg}")


def log_warn(msg: str):
    print(f"[WARN] {msg}")


def log_error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)


def load_env_file():
    """Load environment variables from .env file."""
    global KEYCLOAK_REALM

    if not ENV_FILE.exists():
        return

    log_info(f"Loading environment overrides from {ENV_FILE.name}")
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip().replace('\r', '')
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

    KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", KEYCLOAK_REALM)


def load_cluster_config():
    """Load cluster configuration from config.yaml."""
    global CLUSTER_DOMAIN, ROUTE_GRAFANA, ROUTE_ARGOCD, ROUTE_HEADLAMP

    if not CONFIG_FILE.exists():
        return

    log_info("Loading cluster configuration from config.yaml")
    import yaml
    with open(CONFIG_FILE) as f:
        data = yaml.safe_load(f) or {}

    CLUSTER_DOMAIN = data.get("cluster", {}).get("domain", CLUSTER_DOMAIN)
    ROUTE_GRAFANA = data.get("routes", {}).get("grafana", ROUTE_GRAFANA)
    ROUTE_ARGOCD = data.get("routes", {}).get("argocd", ROUTE_ARGOCD)
    ROUTE_HEADLAMP = data.get("routes", {}).get("headlamp", ROUTE_HEADLAMP)


def require_env_var(var_name: str):
    """Require an environment variable to be set."""
    if not os.environ.get(var_name):
        log_error(f"Environment variable '{var_name}' must be set before running this script.")
        sys.exit(1)


def kubectl_get(*args) -> str:
    """Run kubectl get command."""
    result = subprocess.run(
        ["kubectl", "get"] + list(args),
        capture_output=True, text=True
    )
    return result.stdout.strip()


def kubectl_exec(namespace: str, pod: str, command: str) -> str:
    """Execute command in a pod."""
    result = subprocess.run(
        ["kubectl", "exec", "-n", namespace, pod, "--", "bash", "-c", command],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_keycloak_pod() -> str:
    """Get Keycloak pod name."""
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", "infra", "-l", "app=keycloak",
         "-o", "jsonpath={.items[0].metadata.name}"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def wait_for_keycloak(timeout: int = 300):
    """Wait for Keycloak to be ready."""
    log_info("Waiting for Keycloak to be ready...")
    elapsed = 0
    while elapsed < timeout:
        pod = get_keycloak_pod()
        if pod:
            result = subprocess.run(
                ["kubectl", "get", "pod", "-n", "infra", pod,
                 "-o", "jsonpath={.status.conditions[?(@.type=='Ready')].status}"],
                capture_output=True, text=True
            )
            if result.stdout.strip() == "True":
                log_info("Keycloak is ready.")
                return
        time.sleep(10)
        elapsed += 10

    log_error("Keycloak did not become ready within 5 minutes.")
    sys.exit(1)


def kc_exec(script: str) -> str:
    """Execute kcadm.sh command in Keycloak pod."""
    pod = get_keycloak_pod()
    if not pod:
        log_error("Keycloak pod is not available.")
        sys.exit(1)

    password = os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "")
    command = f"""
export KEYCLOAK_HOME='/opt/bitnami/keycloak'
export PATH="$KEYCLOAK_HOME/bin:$PATH"
export KEYCLOAK_ADMIN_PASSWORD={password!r}
set -euo pipefail
{script}
"""
    result = subprocess.run(
        ["kubectl", "exec", "-n", "infra", pod, "--", "bash", "-c", command],
        capture_output=True, text=True
    )
    if result.returncode != 0 and result.stderr:
        log_warn(f"kc_exec stderr: {result.stderr.strip()}")
    return result.stdout.strip()


def ensure_realm():
    """Ensure Keycloak realm exists."""
    log_info(f"Ensuring realm '{KEYCLOAK_REALM}' exists...")
    kc_exec(f"""
REALM="{KEYCLOAK_REALM}"
kcadm.sh config credentials --server "{KEYCLOAK_URL}" --realm master --user admin --password "$KEYCLOAK_ADMIN_PASSWORD"
if kcadm.sh get realms/$REALM &> /dev/null; then
    echo 'Realm already exists'
else
    kcadm.sh create realms -s realm=$REALM -s enabled=true -s loginWithEmailAllowed=false -s duplicateEmailsAllowed=true -s resetPasswordAllowed=false
    echo 'Realm created'
fi
""")


def create_client(client_id: str, config: dict):
    """Create or update Keycloak client."""
    log_info(f"Ensuring Keycloak client '{client_id}'...")
    import json
    client_json = json.dumps(config)
    # Use Python-interpolated realm so no shell variable quoting issues
    realm = KEYCLOAK_REALM
    script = f"""
kcadm.sh config credentials --server "{KEYCLOAK_URL}" --realm master --user admin --password "$KEYCLOAK_ADMIN_PASSWORD"
EXISTING=$(kcadm.sh get clients -r "{realm}" -q clientId={client_id} --fields clientId 2>/dev/null)
if echo "$EXISTING" | grep -q '"clientId"'; then
    echo 'Client already exists'
else
    cat <<'KCJSON' | kcadm.sh create clients -r "{realm}" -f -
{client_json}
KCJSON
    echo 'Client created'
fi
"""
    kc_exec(script)


def get_client_secret(client_id: str) -> str:
    """Get client secret from Keycloak."""
    realm = KEYCLOAK_REALM
    secret = kc_exec(f"""
kcadm.sh config credentials --server "{KEYCLOAK_URL}" --realm master --user admin --password "$KEYCLOAK_ADMIN_PASSWORD"
CID=$(kcadm.sh get clients -r "{realm}" -q clientId={client_id} --fields id 2>/dev/null | grep '"id"' | head -1 | sed 's/.*: *"//;s/".*//')
if [ -z "$CID" ]; then
    exit 0
fi
kcadm.sh get clients/$CID/client-secret -r "{realm}" 2>/dev/null | grep '"value"' | sed 's/.*: *"//;s/".*//'
""")
    return secret.replace('\r', '').replace('\n', '')


def ensure_secrets():
    """Update Kubernetes secrets with client secrets."""
    grafana_secret = get_client_secret(f"{KEYCLOAK_REALM}-grafana")
    argocd_secret = get_client_secret(f"{KEYCLOAK_REALM}-argocd")
    headlamp_secret = get_client_secret(f"{KEYCLOAK_REALM}-headlamp")

    if grafana_secret:
        import base64
        grafana_admin_password = ""
        try:
            result = subprocess.run(
                ["kubectl", "get", "secret", "grafana-secret", "-n", "infra",
                 "-o", "jsonpath={.data.GRAFANA_ADMIN_PASSWORD}"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                grafana_admin_password = base64.b64decode(result.stdout).decode()
        except Exception:
            pass

        log_info("Updating grafana-secret with refreshed client secret...")
        cmd = ["kubectl", "create", "secret", "generic", "grafana-secret", "-n", "infra",
               f"--from-literal=GRAFANA_OIDC_CLIENT_SECRET={grafana_secret}"]
        if grafana_admin_password:
            cmd.append(f"--from-literal=GRAFANA_ADMIN_PASSWORD={grafana_admin_password}")
        result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
        subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())
    else:
        log_warn("Grafana client secret not available; skipping grafana-secret update.")

    if argocd_secret:
        log_info("Updating argocd-secret with refreshed client secret...")
        cmd = ["kubectl", "create", "secret", "generic", "argocd-secret", "-n", "infra",
               f"--from-literal=OIDC_CLIENT_ID={KEYCLOAK_REALM}-argocd",
               f"--from-literal=OIDC_CLIENT_SECRET={argocd_secret}",
               f"--from-literal=OIDC_ISSUER_URL={KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"]
        result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
        subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())
    else:
        log_warn("ArgoCD client secret not available; skipping argocd-secret update.")

    if headlamp_secret:
        log_info("Updating headlamp-oidc-secret with refreshed client secret...")
        cmd = ["kubectl", "create", "secret", "generic", "headlamp-oidc-secret", "-n", "infra",
               f"--from-literal=OIDC_CLIENT_ID={KEYCLOAK_REALM}-headlamp",
               f"--from-literal=OIDC_CLIENT_SECRET={headlamp_secret}",
               f"--from-literal=OIDC_ISSUER_URL={KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"]
        result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
        subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())
    else:
        log_warn("Headlamp client secret not available; skipping headlamp-oidc-secret update.")


def main():
    load_env_file()
    load_cluster_config()
    require_env_var("KEYCLOAK_ADMIN_PASSWORD")

    wait_for_keycloak()
    ensure_realm()

    grafana_redirects = ["http://localhost:3000/*", f"http://{ROUTE_GRAFANA}.infra.svc.cluster.local:3000/*", f"https://{ROUTE_GRAFANA}.{CLUSTER_DOMAIN}/*"]
    grafana_config = {
        "clientId": f"{KEYCLOAK_REALM}-grafana",
        "enabled": True,
        "protocol": "openid-connect",
        "publicClient": False,
        "standardFlowEnabled": True,
        "redirectUris": grafana_redirects,
        "webOrigins": ["+"],
        "serviceAccountsEnabled": True
    }
    create_client(f"{KEYCLOAK_REALM}-grafana", grafana_config)

    argocd_redirects = ["http://localhost:8080/*", "http://argocd-server.argocd.svc.cluster.local:8080/*", f"https://{ROUTE_ARGOCD}.{CLUSTER_DOMAIN}/auth/callback"]
    argocd_config = {
        "clientId": f"{KEYCLOAK_REALM}-argocd",
        "enabled": True,
        "protocol": "openid-connect",
        "publicClient": False,
        "standardFlowEnabled": True,
        "redirectUris": argocd_redirects,
        "webOrigins": ["+"],
        "serviceAccountsEnabled": True
    }
    create_client(f"{KEYCLOAK_REALM}-argocd", argocd_config)

    headlamp_redirects = ["http://localhost:4466/*", "http://headlamp.infra.svc.cluster.local/*", f"https://{ROUTE_HEADLAMP}.{CLUSTER_DOMAIN}/*"]
    headlamp_config = {
        "clientId": f"{KEYCLOAK_REALM}-headlamp",
        "enabled": True,
        "protocol": "openid-connect",
        "publicClient": False,
        "standardFlowEnabled": True,
        "redirectUris": headlamp_redirects,
        "webOrigins": ["+"],
        "serviceAccountsEnabled": True
    }
    create_client(f"{KEYCLOAK_REALM}-headlamp", headlamp_config)

    ensure_secrets()

    log_info("OAuth recovery completed. Grafana, ArgoCD, and Headlamp clients are refreshed.")


if __name__ == "__main__":
    main()
