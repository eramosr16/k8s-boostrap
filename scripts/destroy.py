#!/usr/bin/env python3
"""Destroy Script - Delete K8s cluster and uninstall K3s entirely."""

from __future__ import annotations

import shutil
import subprocess
import sys


def run_command(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"[INFO] Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=capture)


def confirm_destroy() -> bool:
    """Ask user to confirm destruction."""
    print("[WARN] This will permanently delete the K3s cluster and uninstall K3s from this machine.")
    print("[WARN] All cluster data, workloads, and configurations will be lost.")
    answer = input("Are you sure you want to continue? [y/N]: ").strip().lower()
    return answer in ("y", "yes")


def is_k3s_installed() -> bool:
    """Check if K3s is installed."""
    return shutil.which("k3s") is not None


def stop_k3s_service():
    """Stop K3s service if running."""
    print("[INFO] Stopping K3s service...")
    result = subprocess.run(["systemctl", "is-active", "--quiet", "k3s"], capture_output=True)
    if result.returncode == 0:
        run_command(["sudo", "systemctl", "stop", "k3s"], check=False)
        print("[INFO] K3s service stopped.")
    else:
        print("[INFO] K3s service is not running.")


def run_k3s_uninstall():
    """Run the K3s uninstall script."""
    uninstall_scripts = [
        "/usr/local/bin/k3s-uninstall.sh",
        "/usr/local/bin/k3s-agent-uninstall.sh",
    ]

    found = False
    for script in uninstall_scripts:
        if shutil.which(script) or __import__("pathlib").Path(script).exists():
            print(f"[INFO] Running uninstall script: {script}")
            run_command(["sudo", script], check=False)
            found = True

    if not found:
        print("[WARN] K3s uninstall script not found. Attempting manual cleanup...")
        manual_cleanup()


def manual_cleanup():
    """Manually remove K3s binaries and data if uninstall script is missing."""
    import os

    paths_to_remove = [
        "/usr/local/bin/k3s",
        "/usr/local/bin/k3s-uninstall.sh",
        "/usr/local/bin/k3s-agent-uninstall.sh",
        "/etc/rancher/k3s",
        "/var/lib/rancher/k3s",
        "/var/lib/kubelet",
        "/run/k3s",
        "/run/flannel",
        "/etc/cni/net.d",
        "/opt/cni/bin",
    ]

    for path in paths_to_remove:
        p = __import__("pathlib").Path(path)
        if p.exists():
            print(f"[INFO] Removing {path}...")
            run_command(["sudo", "rm", "-rf", path], check=False)
        else:
            print(f"[INFO] Not found, skipping: {path}")

    # Remove systemd service files
    service_files = [
        "/etc/systemd/system/k3s.service",
        "/etc/systemd/system/k3s.service.env",
        "/etc/systemd/system/k3s-agent.service",
        "/etc/systemd/system/k3s-agent.service.env",
    ]
    for sf in service_files:
        p = __import__("pathlib").Path(sf)
        if p.exists():
            print(f"[INFO] Removing systemd file: {sf}")
            run_command(["sudo", "rm", "-f", sf], check=False)

    run_command(["sudo", "systemctl", "daemon-reload"], check=False)


def remove_kubeconfig():
    """Remove K3s kubeconfig from user home."""
    from pathlib import Path

    kubeconfig = Path.home() / ".kube" / "config"
    if kubeconfig.exists():
        # Check if it's a K3s kubeconfig before removing
        content = kubeconfig.read_text()
        if "k3s" in content or "rancher" in content.lower():
            kubeconfig.unlink()
            print(f"[INFO] Removed kubeconfig at {kubeconfig}")
        else:
            print(f"[INFO] Kubeconfig at {kubeconfig} does not appear to be K3s — skipping removal.")
    else:
        print("[INFO] No kubeconfig found to remove.")


def main():
    print("=== K3s Destroy Script ===")

    if not is_k3s_installed():
        print("[INFO] K3s is not installed on this machine. Nothing to destroy.")
        sys.exit(0)

    if "--yes" not in sys.argv and not confirm_destroy():
        print("[INFO] Destroy cancelled.")
        sys.exit(0)

    stop_k3s_service()
    run_k3s_uninstall()
    remove_kubeconfig()

    print("")
    print("[INFO] K3s cluster destroyed and K3s uninstalled successfully.")
    print("[INFO] You may need to reboot to fully clean up network interfaces.")


if __name__ == "__main__":
    main()
