#!/usr/bin/env python3
"""K3s Bootstrap Script - Install K3s and setup kubectl."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = REPO_ROOT / "config.yaml"


def load_config() -> dict:
    """Load configuration from config.yaml."""
    if not CONFIG_FILE.exists():
        return {}
    import yaml
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f) or {}


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"[INFO] Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def is_k3s_installed() -> bool:
    """Check if K3s is installed."""
    return shutil.which("k3s") is not None


def get_k3s_version() -> str:
    """Get installed K3s version."""
    result = subprocess.run(["k3s", "--version"], capture_output=True, text=True)
    return result.stdout.strip()


def start_k3s_service():
    """Start K3s service if not running."""
    result = subprocess.run(["systemctl", "is-active", "--quiet", "k3s"], capture_output=True)
    if result.returncode == 0:
        print("[INFO] K3s service is running.")
    else:
        print("[INFO] K3s is installed but not running. Starting service...")
        subprocess.run(["sudo", "systemctl", "start", "k3s"])


def install_k3s(config: dict):
    """Install K3s with configuration from config.yaml."""
    print("[INFO] K3s not found. Installing K3s...")

    install_k3s_exec = os.environ.get("INSTALL_K3S_EXEC", "")
    k3s_config = config.get("k3s", {})

    if k3s_config:
        flags = []

        cluster_domain = config.get("cluster", {}).get("domain")
        if cluster_domain:
            flags.append(f"--cluster-domain={cluster_domain}")

        disable_list = k3s_config.get("disable", [])
        for item in disable_list:
            flags.append(f"--disable={item}")

        server_flags = k3s_config.get("serverFlags", [])
        for flag in server_flags:
            flags.append(flag)

        if flags:
            install_k3s_exec = f"server {' '.join(flags)}"
            os.environ["INSTALL_K3S_EXEC"] = install_k3s_exec
            print(f"[INFO] K3s exec flags: {install_k3s_exec}")

    install_script = "https://get.k3s.io"
    subprocess.run(["curl", "-sfL", install_script, "|", "sh", "-"], check=True)
    print("[INFO] K3s installed successfully.")


def setup_kubectl():
    """Setup kubectl configuration."""
    print("[INFO] Setting up kubectl configuration...")
    k3s_kubeconfig = Path("/etc/rancher/k3s/k3s.yaml")
    kubeconfig_dir = Path.home() / ".kube"
    kubeconfig_file = kubeconfig_dir / "config"

    kubeconfig_dir.mkdir(parents=True, exist_ok=True)

    if k3s_kubeconfig.exists():
        if not kubeconfig_file.exists() or kubeconfig_file.read_bytes() != k3s_kubeconfig.read_bytes():
            import shutil as sh
            sh.copy(k3s_kubeconfig, kubeconfig_file)
            kubeconfig_file.chmod(0o600)
            print(f"[INFO] Kubeconfig copied to {kubeconfig_file}")
        else:
            print("[INFO] Kubeconfig already configured.")
    else:
        print(f"[WARN] K3s kubeconfig not found at {k3s_kubeconfig}")


def verify_cluster():
    """Verify cluster connectivity."""
    print("[INFO] Verifying cluster connectivity...")
    subprocess.run(["kubectl", "cluster-info"], check=True)
    print("[INFO] K3s Bootstrap Complete")
    print("[INFO] Run 'kubectl get nodes' to see cluster status.")


def main():
    print("=== K3s Bootstrap Script ===")

    if is_k3s_installed():
        print(f"[INFO] K3s is already installed: {get_k3s_version()}")
        start_k3s_service()
    else:
        config = load_config()
        install_k3s(config)

    setup_kubectl()
    verify_cluster()


if __name__ == "__main__":
    main()
