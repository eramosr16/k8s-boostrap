#!/usr/bin/env python3
"""Setup OAuth with Keycloak for Grafana, ArgoCD, and Headlamp."""

from __future__ import annotations

import os
import subprocess
import sys
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
                ["kubectl", "exec", "-n", "infra", pod, "--",
                 "curl", "-sf", f"{KEYCLOAK_URL}/health/ready"],
                capture_output=True
            )
            if result.returncode == 0:
                log_info("Keycloak is ready.")
                return
        import time
        time.sleep(10)
        elapsed += 10

    log_error("Keycloak did not become ready within 5 minutes.")
    sys.exit(1)


def kc_exec(script: str) -> str:
    """Execute kcadm command in Keycloak pod."""
    pod = get_keycloak_pod()
    if not pod:
        log_error("Keycloak pod is not available.")
        sys.exit(1)

    env = os.environ.copy()
    command = f"""
export KEYCLOAK_HOME='/opt/keycloak'
export PATH="$KEYCLOAK_HOME/bin:$PATH"
set -euo pipefail
{script}
"""
    result = subprocess.run(
        ["kubectl", "exec", "-n", "infra", pod, "--", "bash", "-c", command],
        capture_output=True, text=True, env=env
    )
    return result.stdout.strip()


def ensure_realm():
    """Ensure Keycloak realm exists."""
    log_info(f"Ensuring realm '{KEYCLOAK_REALM}' exists...")
    kc_exec(f"""
REALM='{KEYCLOAK_REALM}'
kcadm config credentials --server '{KEYCLOAK_URL}' --realm master --user admin --password $KEYCLOAK_ADMIN_PASSWORD
if kcadm get realms/$REALM &> /dev/null; then
    echo 'Realm already exists'
else
    kcadm create realms -s realm=$REALM -s enabled=true -s loginWithEmailAllowed=false -s duplicateEmailsAllowed=true -s resetPasswordAllowed=false
    echo 'Realm created'
fi
""")


def create_client(client_id: str, params: str):
    """Create or update Keycloak client."""
    log_info(f"Ensuring Keycloak client '{client_id}'...")
    kc_exec(f"""
REALM='{KEYCLOAK_REALM}'
kcadm config credentials --server '{KEYCLOAK_URL}' --realm master --user admin --password $KEYCLOAK_ADMIN_PASSWORD
kcadm create clients -r '$REALM' -s clientId={client_id} {params} || true
""")


def get_client_secret(client_id: str) -> str:
    """Get client secret from Keycloak."""
    secret = kc_exec(f"""
REALM='{KEYCLOAK_REALM}'
kcadm config credentials --server '{KEYCLOAK_URL}' --realm master --user admin --password $KEYCLOAK_ADMIN_PASSWORD
CID=$(kcadm get clients -r '$REALM' -q clientId={client_id} --fields id 2>/dev/null | jq -r '.[0].id' 2>/dev/null)
if [ -z "$CID" ]; then
    exit 0
fi
kcadm get clients/$CID/client-secret -r '$REALM' 2>/dev/null | jq -r '.value'
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

    grafana_redirects = f'["http://localhost:3000/*","http://{ROUTE_GRAFANA}.infra.svc.cluster.local:3000/*","https://{ROUTE_GRAFANA}.{CLUSTER_DOMAIN}/*"]'
    grafana_params = f'-s clientId={KEYCLOAK_REALM}-grafana -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s redirectUris={grafana_redirects} -s webOrigins=["+"] -s serviceAccountsEnabled=true'
    create_client(f"{KEYCLOAK_REALM}-grafana", grafana_params)

    argocd_redirects = f'["http://localhost:8080/*","http://argocd-server.argocd.svc.cluster.local:8080/*","https://{ROUTE_ARGOCD}.{CLUSTER_DOMAIN}/auth/callback"]'
    argocd_params = f'-s clientId={KEYCLOAK_REALM}-argocd -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s redirectUris={argocd_redirects} -s webOrigins=["+"] -s serviceAccountsEnabled=true'
    create_client(f"{KEYCLOAK_REALM}-argocd", argocd_params)

    headlamp_redirects = f'["http://localhost:4466/*","http://headlamp.infra.svc.cluster.local/*","https://{ROUTE_HEADLAMP}.{CLUSTER_DOMAIN}/*"]'
    headlamp_params = f'-s clientId={KEYCLOAK_REALM}-headlamp -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s redirectUris={headlamp_redirects} -s webOrigins=["+"] -s serviceAccountsEnabled=true'
    create_client(f"{KEYCLOAK_REALM}-headlamp", headlamp_params)

    ensure_secrets()

    log_info("OAuth recovery completed. Grafana, ArgoCD, and Headlamp clients are refreshed.")


if __name__ == "__main__":
    main()
