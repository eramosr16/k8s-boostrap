#!/usr/bin/env python3
"""Setup Routes - Patch Traefik IngressRoute hostnames using config.yaml.

This is a post-installation script. Run it after ArgoCD has synced and all
services are up. It patches the live IngressRoute resources in the cluster
so that hostnames match the domain and route prefixes defined in config.yaml.

Example:
    .venv/bin/python scripts/setup_routes.py
    .venv/bin/python scripts/setup_routes.py --dry-run
    .venv/bin/python scripts/setup_routes.py --verify-only
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = REPO_ROOT / "config.yaml"

# Defaults (same as mydomain.com placeholders in the YAML files)
CLUSTER_DOMAIN = "mydomain.com"
ROUTE_ARGOCD = "argocd"
ROUTE_GRAFANA = "grafana"
ROUTE_HEADLAMP = "headlamp"
ROUTE_KEYCLOAK = "auth"
ROUTE_LOKI = "logs"


def log_info(msg: str):
    print(f"[INFO] {msg}")


def log_warn(msg: str):
    print(f"[WARN] {msg}")


def log_error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)


def log_ok(msg: str):
    print(f"[ OK ] {msg}")


def log_fail(msg: str):
    print(f"[FAIL] {msg}")


def load_config() -> None:
    """Load cluster configuration from config.yaml."""
    global CLUSTER_DOMAIN, ROUTE_ARGOCD, ROUTE_GRAFANA, ROUTE_HEADLAMP, ROUTE_KEYCLOAK, ROUTE_LOKI

    if not CONFIG_FILE.exists():
        log_warn(f"config.yaml not found at {CONFIG_FILE}; using defaults.")
        return

    log_info("Loading cluster configuration from config.yaml")
    import yaml
    with open(CONFIG_FILE) as f:
        data = yaml.safe_load(f) or {}

    CLUSTER_DOMAIN = data.get("cluster", {}).get("domain", CLUSTER_DOMAIN)
    ROUTE_ARGOCD   = data.get("routes", {}).get("argocd",   ROUTE_ARGOCD)
    ROUTE_GRAFANA  = data.get("routes", {}).get("grafana",  ROUTE_GRAFANA)
    ROUTE_HEADLAMP = data.get("routes", {}).get("headlamp", ROUTE_HEADLAMP)
    ROUTE_KEYCLOAK = data.get("routes", {}).get("keycloak", ROUTE_KEYCLOAK)
    ROUTE_LOKI     = data.get("routes", {}).get("loki",     ROUTE_LOKI)


# Map of IngressRoute resource -> expected hostname
# Each entry: (name, namespace, expected_host)
def expected_routes() -> list[tuple[str, str, str]]:
    return [
        ("argocd",   "argocd", f"{ROUTE_ARGOCD}.{CLUSTER_DOMAIN}"),
        ("grafana",  "infra",  f"{ROUTE_GRAFANA}.{CLUSTER_DOMAIN}"),
        ("headlamp", "infra",  f"{ROUTE_HEADLAMP}.{CLUSTER_DOMAIN}"),
        ("keycloak", "infra",  f"{ROUTE_KEYCLOAK}.{CLUSTER_DOMAIN}"),
    ]


def get_current_host(name: str, namespace: str) -> str | None:
    """Get the current Host match value from a live IngressRoute."""
    result = subprocess.run(
        [
            "kubectl", "get", "ingressroute", name,
            "-n", namespace,
            "-o", "jsonpath={.spec.routes[0].match}",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def patch_host(name: str, namespace: str, new_host: str, dry_run: bool) -> bool:
    """Patch the Host match rule of an IngressRoute via a strategic JSON merge patch."""
    # Traefik IngressRoute uses .spec.routes[0].match = Host(`hostname`)
    new_match = f"Host(`{new_host}`)"
    patch = json.dumps({
        "spec": {
            "routes": [{"match": new_match, "kind": "Rule"}]
        }
    })

    cmd = [
        "kubectl", "patch", "ingressroute", name,
        "-n", namespace,
        "--type", "merge",
        "-p", patch,
    ]

    if dry_run:
        log_info(f"[DRY-RUN] Would patch {namespace}/{name}: {new_match}")
        return True

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log_error(f"Failed to patch {namespace}/{name}: {result.stderr.strip()}")
        return False

    return True


def verify_routes() -> bool:
    """Check that all IngressRoutes have the expected hostnames. Returns True if all match."""
    log_info(f"Verifying IngressRoute hostnames for domain: {CLUSTER_DOMAIN}")
    all_ok = True
    for name, namespace, expected_host in expected_routes():
        current = get_current_host(name, namespace)
        if current is None:
            log_fail(f"{namespace}/{name}: IngressRoute not found on cluster")
            all_ok = False
            continue

        expected_match = f"Host(`{expected_host}`)"
        if current == expected_match:
            log_ok(f"{namespace}/{name}: {current}")
        else:
            log_fail(f"{namespace}/{name}: current={current!r}  expected={expected_match!r}")
            all_ok = False

    return all_ok


def setup_routes(dry_run: bool) -> bool:
    """Patch all IngressRoutes to use the hostnames from config.yaml."""
    log_info(f"Patching IngressRoute hostnames for domain: {CLUSTER_DOMAIN}")
    all_ok = True
    for name, namespace, expected_host in expected_routes():
        current = get_current_host(name, namespace)
        if current is None:
            log_warn(f"{namespace}/{name}: IngressRoute not found on cluster — skipping")
            all_ok = False
            continue

        expected_match = f"Host(`{expected_host}`)"
        if current == expected_match:
            log_ok(f"{namespace}/{name}: already correct ({current})")
            continue

        log_info(f"{namespace}/{name}: {current!r} -> {expected_match!r}")
        ok = patch_host(name, namespace, expected_host, dry_run)
        if ok and not dry_run:
            log_ok(f"{namespace}/{name}: patched successfully")
        elif not ok:
            all_ok = False

    return all_ok


def main():
    parser = argparse.ArgumentParser(
        description="Patch Traefik IngressRoute hostnames from config.yaml"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be patched without making changes",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify current routes without patching",
    )
    args = parser.parse_args()

    print("=== Setup Routes ===")
    load_config()
    log_info(f"Domain:   {CLUSTER_DOMAIN}")
    log_info(f"Routes:   argocd={ROUTE_ARGOCD}, grafana={ROUTE_GRAFANA}, "
             f"headlamp={ROUTE_HEADLAMP}, keycloak={ROUTE_KEYCLOAK}")

    if args.verify_only:
        ok = verify_routes()
        sys.exit(0 if ok else 1)

    ok = setup_routes(dry_run=args.dry_run)

    if not args.dry_run:
        print()
        verify_routes()

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
