#!/usr/bin/env python3
"""ArgoCD Installation Script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARGOCD_NAMESPACE = "argocd"
ARGOCD_MANIFEST_URL = "https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"
ARGOCD_SERVER_SERVICE = REPO_ROOT / "infra" / "services" / "observability" / "argocd" / "argocd-server-service.yaml"


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"[INFO] Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def check_kubectl():
    """Check if kubectl is available."""
    try:
        subprocess.run(["which", "kubectl"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("[ERROR] kubectl is not installed. Run scripts/bootstrap.sh first.")
        sys.exit(1)


def create_namespace():
    """Create ArgoCD namespace."""
    print("[INFO] Creating argocd namespace...")
    subprocess.run([
        "kubectl", "create", "namespace", ARGOCD_NAMESPACE,
        "--dry-run=client", "-o", "yaml"
    ], capture_output=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=b"", capture_output=True)


def install_argocd():
    """Install ArgoCD."""
    print("[INFO] Installing ArgoCD...")
    print("[INFO] Cleaning existing argocd-server service before reinstall...")
    subprocess.run(["kubectl", "delete", "svc", "argocd-server", "-n", ARGOCD_NAMESPACE, "--ignore-not-found"], capture_output=True)

    print("[INFO] Applying ArgoCD manifests...")
    subprocess.run(["kubectl", "apply", "-n", ARGOCD_NAMESPACE, "-f", ARGOCD_MANIFEST_URL], check=True)

    print("[INFO] Removing the upstream argocd-server service and applying the custom 8080-only version...")
    subprocess.run(["kubectl", "delete", "svc", "argocd-server", "-n", ARGOCD_NAMESPACE, "--ignore-not-found"], capture_output=True)

    if ARGOCD_SERVER_SERVICE.exists():
        subprocess.run(["kubectl", "apply", "-n", ARGOCD_NAMESPACE, "-f", str(ARGOCD_SERVER_SERVICE)], check=True)
    else:
        print(f"[WARN] Custom argocd-server-service.yaml not found at {ARGOCD_SERVER_SERVICE}")


def wait_for_argocd():
    """Wait for ArgoCD to be ready."""
    print("[INFO] Waiting for ArgoCD to be ready...")
    subprocess.run([
        "kubectl", "wait", "--for=condition=ready", "pod",
        "-l", "app.kubernetes.io/name=argocd-server",
        "-n", ARGOCD_NAMESPACE, "--timeout=300s"
    ], check=True)


def get_admin_password() -> str:
    """Retrieve initial admin password."""
    result = subprocess.run([
        "kubectl", "-n", ARGOCD_NAMESPACE, "get", "secret", "argocd-initial-admin-secret",
        "-o", "jsonpath={.data.password}"
    ], capture_output=True, text=True, check=True)

    import base64
    return base64.b64decode(result.stdout).decode()


def main():
    print("=== ArgoCD Installation Script ===")

    check_kubectl()
    create_namespace()
    install_argocd()
    wait_for_argocd()

    password = get_admin_password()

    print("\n=== ArgoCD Installation Complete ===")
    print("UI Access: http://localhost:8080")
    print("Username: admin")
    print(f"Password: {password}")
    print("\nTo access ArgoCD UI, run:")
    print("  kubectl port-forward svc/argocd-server -n argocd 8080:8080")


if __name__ == "__main__":
    main()
