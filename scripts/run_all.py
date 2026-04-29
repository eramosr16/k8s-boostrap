#!/usr/bin/env python3
"""K8s Cluster Bootstrap - Full bootstrap process."""

from __future__ import annotations

import getpass
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = REPO_ROOT / "config.yaml"
ENV_FILE = REPO_ROOT / "env.example"
ENV_FILE_LOCAL = REPO_ROOT / ".env"

CLUSTER_DOMAIN = "cluster.local"
KEYCLOAK_REALM = "infra"
ROUTE_ARGOCD = "argocd"
ROUTE_GRAFANA = "grafana"
ROUTE_HEADLAMP = "headlamp"
ROUTE_KEYCLOAK = "keycloak"
KEYCLOAK_HOST_IP = ""
TRAEFIK_EMAIL = ""
ARGOCD_CLI_VERSION = "v2.9.11"
HEALTH_CHECK_TIMEOUT = 300
HEALTH_CHECK_INTERVAL = 10
KEYCLOAK_TIMEOUT = 180
DEFAULT_DNS_FORWARDERS = ["8.8.8.8", "1.1.1.1"]

# Colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"


def log_info(msg: str):
    print(f"{GREEN}[INFO]{NC} {msg}")


def log_warn(msg: str):
    print(f"{YELLOW}[WARN]{NC} {msg}")


def log_error(msg: str):
    print(f"{RED}[ERROR]{NC} {msg}", file=sys.stderr)


def run_command(cmd: list[str], check: bool = True, capture: bool = False, input_data: bytes = None) -> subprocess.CompletedProcess:
    """Run a shell command."""
    if not capture:
        log_info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture, text=not isinstance(input_data, bytes), input=input_data)
    if check and result.returncode != 0:
        if capture:
            log_error(f"Command failed: {' '.join(cmd)}")
            log_error(f"stdout: {result.stdout}")
            log_error(f"stderr: {result.stderr}")
        sys.exit(1)
    return result


def command_exists(cmd: str) -> bool:
    """Check if a command exists."""
    return subprocess.run(["which", cmd], capture_output=True).returncode == 0


def check_requirements():
    """Check required dependencies."""
    missing = []
    for tool in ["python3", "docker"]:
        if not command_exists(tool):
            log_error(f"Dependency '{tool}' is missing. Install it before running this script.")
            missing.append(tool)
            continue
        if tool == "docker":
            result = subprocess.run(["docker", "info"], capture_output=True)
            if result.returncode != 0:
                log_warn("Docker binary is present but the daemon is unreachable. Ensure Docker is running if this script needs it.")

    if missing:
        sys.exit(1)


def load_config() -> dict:
    """Load configuration from config.yaml."""
    global CLUSTER_DOMAIN, KEYCLOAK_REALM, ROUTE_ARGOCD, ROUTE_GRAFANA, ROUTE_HEADLAMP, ROUTE_KEYCLOAK, KEYCLOAK_HOST_IP

    if not CONFIG_FILE.exists():
        return {}

    import yaml
    with open(CONFIG_FILE) as f:
        data = yaml.safe_load(f) or {}

    CLUSTER_DOMAIN = data.get("cluster", {}).get("domain", CLUSTER_DOMAIN)
    KEYCLOAK_REALM = data.get("keycloak", {}).get("realm", KEYCLOAK_REALM)
    ROUTE_ARGOCD = data.get("routes", {}).get("argocd", ROUTE_ARGOCD)
    ROUTE_GRAFANA = data.get("routes", {}).get("grafana", ROUTE_GRAFANA)
    ROUTE_HEADLAMP = data.get("routes", {}).get("headlamp", ROUTE_HEADLAMP)
    ROUTE_KEYCLOAK = data.get("routes", {}).get("keycloak", ROUTE_KEYCLOAK)
    KEYCLOAK_HOST_IP = data.get("cluster", {}).get("hostIP", KEYCLOAK_HOST_IP)

    os.environ["CLUSTER_DOMAIN"] = CLUSTER_DOMAIN
    os.environ["KEYCLOAK_REALM"] = KEYCLOAK_REALM
    os.environ["ROUTE_ARGOCD"] = ROUTE_ARGOCD
    os.environ["ROUTE_GRAFANA"] = ROUTE_GRAFANA
    os.environ["ROUTE_HEADLAMP"] = ROUTE_HEADLAMP
    os.environ["ROUTE_KEYCLOAK"] = ROUTE_KEYCLOAK
    os.environ["KEYCLOAK_HOST_IP"] = KEYCLOAK_HOST_IP
    os.environ["TRAEFIK_EMAIL"] = TRAEFIK_EMAIL

    return data


def load_env_file():
    """Load environment variables from .env file."""
    env_file = ENV_FILE_LOCAL if ENV_FILE_LOCAL.exists() else ENV_FILE
    if not env_file.exists():
        return

    log_info(f"Loading environment overrides from {env_file.name}")
    with open(env_file) as f:
        for line in f:
            line = line.strip().replace('\r', '')
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', line):
                continue
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()


def require_config_update():
    """Require that config.yaml has been modified."""
    if not subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--is-inside-work-tree"], capture_output=True).returncode == 0:
        log_warn("Unable to validate git status for config.yaml; ensure it's customized before running.")
        return

    result = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--short", "--", "config.yaml"], capture_output=True, text=True)
    if not result.stdout.strip():
        log_error("config.yaml has not changed. Please edit it with your cluster values before running this script.")
        sys.exit(1)


def check_dns_forwarders():
    """Check DNS forwarders."""
    if not command_exists("nslookup"):
        log_warn("nslookup is unavailable; skipping DNS forwarder reachability check.")
        return

    failed = 0
    for resolver in DEFAULT_DNS_FORWARDERS:
        result = subprocess.run(["nslookup", "github.com", resolver], capture_output=True)
        if result.returncode == 0:
            log_info(f"DNS forwarder {resolver} can resolve github.com.")
        else:
            log_warn(f"DNS forwarder {resolver} cannot reach github.com.")
            failed = 1

    if failed:
        log_warn("Verify connectivity to the DNS forwarders above if CoreDNS still cannot reach external names.")


def prompt_secret(name: str, var_name: str, description: str, allow_empty: bool = False) -> str:
    """Prompt for a secret value."""
    prefilled = os.environ.get(var_name, "")
    if prefilled:
        return prefilled

    log_warn(f"Environment variable '{var_name}' is not set; prompting for '{name}'.")
    prompt_message = f"{description} [{var_name}]: "

    while True:
        try:
            value = getpass.getpass(prompt=prompt_message)
        except (EOFError, KeyboardInterrupt):
            log_error(f"Failed to read {name}")
            sys.exit(1)

        value = value.replace('\r', '')
        if not value:
            if allow_empty:
                return ""
            log_error(f"{name} cannot be empty. Please try again.")
            continue
        return value


def mask_value(value: str) -> str:
    """Mask a value for logging."""
    if not value:
        return "[empty]"
    prefix = value[:4]
    return f"[{prefix}]****"


def install_k3s():
    """Install K3s."""
    log_info("Checking for K3s...")

    if command_exists("k3s"):
        log_info(f"K3s is already installed: {subprocess.run(['k3s', '--version'], capture_output=True, text=True).stdout.strip()}")
        result = subprocess.run(["systemctl", "is-active", "--quiet", "k3s"], capture_output=True)
        if result.returncode == 0:
            log_info("K3s service is running.")
        else:
            log_warn("K3s is installed but not running. Starting service...")
            subprocess.run(["sudo", "systemctl", "start", "k3s"])
    else:
        log_info("K3s not found. Installing K3s...")
        subprocess.run(["curl", "-sfL", "https://get.k3s.io", "|", "sh", "-"], check=True)
        log_info("K3s installed successfully.")

    log_info("Setting up kubectl configuration...")
    k3s_kubeconfig = Path("/etc/rancher/k3s/k3s.yaml")
    kubeconfig_dir = Path.home() / ".kube"
    kubeconfig_file = kubeconfig_dir / "config"

    kubeconfig_dir.mkdir(parents=True, exist_ok=True)

    if k3s_kubeconfig.exists():
        if not kubeconfig_file.exists() or kubeconfig_file.read_bytes() != k3s_kubeconfig.read_bytes():
            import shutil
            shutil.copy(k3s_kubeconfig, kubeconfig_file)
            kubeconfig_file.chmod(0o600)
            log_info(f"Kubeconfig copied to {kubeconfig_file}")
        else:
            log_info("Kubeconfig already configured.")
    else:
        log_warn(f"K3s kubeconfig not found at {k3s_kubeconfig}")

    os.environ["KUBECONFIG"] = str(kubeconfig_file)
    log_info("Verifying cluster connectivity...")
    subprocess.run(["kubectl", "cluster-info"], check=True)
    log_info("K3s setup complete.")


def prompt_confirmation(prompt: str) -> bool:
    """Prompt for yes/no confirmation."""
    if not sys.stdin.isatty():
        log_warn("Non-interactive shell detected; defaulting to 'no'.")
        return False

    while True:
        try:
            response = input(f"{prompt} [y/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False

        if response in ("y", "yes"):
            return True
        if response in ("n", "no", ""):
            return False
        print("Please answer yes or no.")


def reset_existing_argocd():
    """Reset existing ArgoCD installation."""
    result = subprocess.run(["kubectl", "get", "namespace", "argocd"], capture_output=True)
    if result.returncode != 0:
        return

    log_warn("An existing ArgoCD installation was detected.")
    if not prompt_confirmation("Delete the current ArgoCD namespace and all cached applications so we can start fresh?"):
        log_info("Keeping existing ArgoCD installation as requested.")
        return

    log_info("Deleting namespace argocd to clear previous ArgoCD resources...")
    subprocess.run(["kubectl", "delete", "namespace", "argocd", "--ignore-not-found"])
    while True:
        result = subprocess.run(["kubectl", "get", "namespace", "argocd"], capture_output=True)
        if result.returncode != 0:
            break
        time.sleep(2)
    log_info("ArgoCD namespace removed. A fresh installation will be applied next.")


def install_argocd():
    """Install ArgoCD."""
    log_info("Installing ArgoCD...")

    subprocess.run(["kubectl", "create", "namespace", "argocd", "--dry-run=client", "-o", "yaml"], capture_output=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=b"", capture_output=True)

    log_info("Removing any existing argocd-server service before installing upstream manifests...")
    subprocess.run(["kubectl", "delete", "svc", "argocd-server", "-n", "argocd", "--ignore-not-found"])

    argocd_manifest = "https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"
    subprocess.run(["kubectl", "apply", "--server-side", "--force-conflicts", "-n", "argocd", "-f", argocd_manifest], check=True)

    log_info("Re-applying the custom 8080-only argocd-server service...")
    argocd_service = REPO_ROOT / "infra" / "services" / "observability" / "argocd" / "argocd-server-service.yaml"
    subprocess.run(["kubectl", "delete", "svc", "argocd-server", "-n", "argocd", "--ignore-not-found"])
    if argocd_service.exists():
        subprocess.run(["kubectl", "apply", "-n", "argocd", "-f", str(argocd_service)])
    else:
        log_warn(f"Custom argocd-server-service.yaml not found at {argocd_service}")

    log_info("Waiting for ArgoCD to be ready...")
    subprocess.run(["kubectl", "wait", "--for=condition=ready", "pod", "-l", "app.kubernetes.io/name=argocd-server",
                   "-n", "argocd", "--timeout=300s"], check=True)

    log_info("ArgoCD installed successfully.")


def install_argocd_cli():
    """Install ArgoCD CLI."""
    log_info("Ensuring ArgoCD CLI is installed...")

    if command_exists("argocd"):
        log_info(f"argocd CLI already available at {subprocess.run(['which', 'argocd'], capture_output=True, text=True).stdout.strip()}")
        return

    version = os.environ.get("ARGOCD_CLI_VERSION", ARGOCD_CLI_VERSION)
    os_type = "linux"
    arch = subprocess.run(["uname", "-m"], capture_output=True, text=True).stdout.strip()
    if arch == "x86_64":
        arch = "amd64"
    elif arch in ("aarch64", "arm64"):
        arch = "arm64"

    download_url = f"https://github.com/argoproj/argo-cd/releases/download/{version}/argocd-{os_type}-{arch}"
    tmpfile = "/tmp/argocd-cli-download"

    for attempt in range(1, 4):
        result = subprocess.run(["curl", "-fsSL", "-o", tmpfile, download_url], capture_output=True)
        if result.returncode == 0 and Path(tmpfile).stat().st_size > 0:
            break
        log_warn(f"Attempt {attempt} failed to download argocd CLI, retrying...")
        time.sleep(1)

    if not Path(tmpfile).exists() or Path(tmpfile).stat().st_size == 0:
        log_error(f"Failed to download argocd CLI from {download_url}")
        sys.exit(1)

    os.chmod(tmpfile, 0o755)
    target = "/usr/local/bin/argocd"
    try:
        if os.access(os.path.dirname(target), os.W_OK):
            os.rename(tmpfile, target)
        else:
            subprocess.run(["sudo", "mv", tmpfile, target])
    except Exception:
        log_error("Failed to install argocd CLI")
        sys.exit(1)

    log_info(f"argocd CLI installed at {target}")


def prompt_secrets():
    """Prompt for all secrets."""
    global TRAEFIK_EMAIL

    log_info("=== Credential Setup ===")
    log_info("Please enter credentials for all services.")
    print()

    credentials = [
        ("PostgreSQL Password", "POSTGRES_PASSWORD", "Enter PostgreSQL password", False),
        ("Redis Password", "REDIS_PASSWORD", "Enter Redis password", False),
        ("RabbitMQ Username", "RABBITMQ_DEFAULT_USER", "Enter RabbitMQ username", False),
        ("RabbitMQ Password", "RABBITMQ_DEFAULT_PASS", "Enter RabbitMQ password", False),
        ("Keycloak Admin Password", "KEYCLOAK_ADMIN_PASSWORD", "Enter Keycloak admin password", False),
        ("GitHub Personal Access Token", "GITHUB_PAT", "Enter GitHub PAT for private repos", False),
        ("Let's Encrypt Email", "LETS_ENCRYPT_EMAIL", "Enter Let's Encrypt email for Traefik ACME", False),
        ("AWS Access Key ID", "AWS_ACCESS_KEY_ID", "Enter AWS access key (or press Enter to skip)", True),
        ("AWS Secret Access Key", "AWS_SECRET_ACCESS_KEY", "Enter AWS secret key (or press Enter to skip)", True),
        ("AWS Account ID", "AWS_ACCOUNT_ID", "Enter AWS account ID (or press Enter to skip)", True),
        ("AWS Region", "AWS_REGION", "Enter AWS region (default us-east-1 if unset)", True),
    ]

    for name, var_name, prompt, allow_empty in credentials:
        value = prompt_secret(name, var_name, prompt, allow_empty)
        os.environ[var_name] = value

    log_info("Credentials collected.")

    if not os.environ.get("TRAEFIK_EMAIL") and os.environ.get("LETS_ENCRYPT_EMAIL"):
        TRAEFIK_EMAIL = os.environ["LETS_ENCRYPT_EMAIL"]
        os.environ["TRAEFIK_EMAIL"] = TRAEFIK_EMAIL

    if TRAEFIK_EMAIL:
        log_info(f"Let's Encrypt email recorded as {mask_value(TRAEFIK_EMAIL)}")

    if not os.environ.get("AWS_REGION"):
        os.environ["AWS_REGION"] = "us-east-1"
        log_info("AWS_REGION not set; defaulting to us-east-1")


def create_secrets():
    """Create Kubernetes secrets."""
    log_info("Creating Kubernetes secrets...")

    subprocess.run(["kubectl", "create", "namespace", "infra", "--dry-run=client", "-o", "yaml"])
    subprocess.run(["kubectl", "apply", "-f", "-"], input=b"", capture_output=True)

    # PostgreSQL secret
    cmd = ["kubectl", "create", "secret", "generic", "postgres-secret", "-n", "infra",
           "--from-literal=POSTGRES_DB=postgres",
           "--from-literal=POSTGRES_USER=postgres",
           f"--from-literal=POSTGRES_PASSWORD={os.environ.get('POSTGRES_PASSWORD', '')}"]
    result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())

    # Redis secret
    cmd = ["kubectl", "create", "secret", "generic", "redis-secret", "-n", "infra",
           f"--from-literal=REDIS_PASSWORD={os.environ.get('REDIS_PASSWORD', '')}"]
    result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())

    # RabbitMQ secret
    cmd = ["kubectl", "create", "secret", "generic", "rabbitmq-secret", "-n", "infra",
           f"--from-literal=RABBITMQ_DEFAULT_USER={os.environ.get('RABBITMQ_DEFAULT_USER', '')}",
           f"--from-literal=RABBITMQ_DEFAULT_PASS={os.environ.get('RABBITMQ_DEFAULT_PASS', '')}"]
    result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())

    # Keycloak secret
    cmd = ["kubectl", "create", "secret", "generic", "keycloak-secret", "-n", "infra",
           f"--from-literal=KEYCLOAK_ADMIN_PASSWORD={os.environ.get('KEYCLOAK_ADMIN_PASSWORD', '')}",
           "--from-literal=KC_BOOTSTRAP_ADMIN_USERNAME=admin",
           f"--from-literal=KC_BOOTSTRAP_ADMIN_PASSWORD={os.environ.get('KEYCLOAK_ADMIN_PASSWORD', '')}"]
    result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())

    # ArgoCD namespace
    subprocess.run(["kubectl", "create", "namespace", "argocd", "--dry-run=client", "-o", "yaml"])
    subprocess.run(["kubectl", "apply", "-f", "-"], input=b"", capture_output=True)

    # ArgoCD GitHub secret
    cmd = ["kubectl", "create", "secret", "generic", "argocd-private-github", "-n", "argocd",
           "--from-literal=username=git",
           f"--from-literal=password={os.environ.get('GITHUB_PAT', '')}"]
    result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())

    # Traefik ACME secret
    cmd = ["kubectl", "create", "secret", "generic", "traefik-acme-secret", "-n", "kube-system",
           f"--from-literal=email={os.environ.get('LETS_ENCRYPT_EMAIL', '')}"]
    result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())

    # Grafana secret
    cmd = ["kubectl", "create", "secret", "generic", "grafana-secret", "-n", "infra",
           f"--from-literal=admin-password={os.environ.get('GRAFANA_ADMIN_PASSWORD', '')}"]
    result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())

    # Headlamp OIDC secret
    cmd = ["kubectl", "create", "secret", "generic", "headlamp-oidc-secret", "-n", "infra",
           "--from-literal=OIDC_CLIENT_ID=headlamp",
           f"--from-literal=OIDC_ISSUER_URL=http://keycloak.infra.svc.cluster.local:8080/realms/{KEYCLOAK_REALM}"]
    result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())

    # AWS secrets if available
    if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
        cmd = ["kubectl", "create", "secret", "generic", "aws-ecr-secret", "-n", "infra",
               f"--from-literal=aws-access-key-id={os.environ.get('AWS_ACCESS_KEY_ID', '')}",
               f"--from-literal=aws-secret-access-key={os.environ.get('AWS_SECRET_ACCESS_KEY', '')}"]
        result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
        subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())

        if os.environ.get("AWS_ACCOUNT_ID") and os.environ.get("AWS_REGION"):
            cmd = ["kubectl", "create", "secret", "generic", "ecr-refresh-aws-creds", "-n", "infra",
                   f"--from-literal=AWS_ACCOUNT_ID={os.environ.get('AWS_ACCOUNT_ID', '')}",
                   f"--from-literal=AWS_REGION={os.environ.get('AWS_REGION', '')}",
                   f"--from-literal=AWS_ACCESS_KEY_ID={os.environ.get('AWS_ACCESS_KEY_ID', '')}",
                   f"--from-literal=AWS_SECRET_ACCESS_KEY={os.environ.get('AWS_SECRET_ACCESS_KEY', '')}"]
            result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
            subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())
            log_info("ECR refresh credentials secret created.")
        else:
            log_warn("Skipping ecr-refresh-aws-creds secret creation; AWS credentials incomplete.")
    else:
        log_warn("Skipping ecr-registry secret creation; AWS credentials incomplete.")

    log_info("Secrets created.")
    create_ecr_registry_secret()


def create_ecr_registry_secret():
    """Create ECR registry pull secret."""
    if not os.environ.get("AWS_ACCESS_KEY_ID") or not os.environ.get("AWS_SECRET_ACCESS_KEY"):
        log_warn("Skipping ecr-registry secret creation; AWS credentials incomplete.")
        return

    if not command_exists("docker"):
        log_warn("docker binary missing; cannot create ecr-registry secret automatically.")
        return

    log_info("Creating initial ecr-registry pull secret via dockerized aws CLI...")
    aws_account_id = os.environ.get("AWS_ACCOUNT_ID", "")
    aws_region = os.environ.get("AWS_REGION", "")
    docker_server = f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com"
    aws_cli_image = "public.ecr.aws/aws-cli/aws-cli:2.27.41"

    result = subprocess.run([
        "docker", "run", "--rm", "-i",
        "-e", f"AWS_ACCESS_KEY_ID={os.environ.get('AWS_ACCESS_KEY_ID', '')}",
        "-e", f"AWS_SECRET_ACCESS_KEY={os.environ.get('AWS_SECRET_ACCESS_KEY', '')}",
        "-e", f"AWS_REGION={aws_region}",
        aws_cli_image,
        "ecr", "get-login-password"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        log_warn("Failed to fetch ECR login password via docker; ecr-registry secret creation skipped.")
        return

    token = result.stdout.strip()

    cmd = ["kubectl", "create", "secret", "docker-registry", "ecr-registry",
           "--namespace", "default",
           f"--docker-server={docker_server}",
           "--docker-username=AWS",
           f"--docker-password={token}"]
    result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
    subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())
    log_info("Initial ecr-registry pull secret ensured.")


def wait_for_postgres():
    """Wait for PostgreSQL to be ready."""
    log_info("Waiting for PostgreSQL to be ready...")
    subprocess.run(["kubectl", "wait", "--for=condition=Ready", "pod", "-l", "app=postgres",
                   "-n", "infra", "--timeout=180s"], check=True)


def create_keycloak_database():
    """Create Keycloak database in PostgreSQL."""
    log_info("Ensuring the Keycloak database exists in PostgreSQL...")
    wait_for_postgres()

    result = subprocess.run(["kubectl", "get", "pods", "-n", "infra", "-l", "app=postgres",
                            "-o", "jsonpath={.items[0].metadata.name}"], capture_output=True, text=True)
    if not result.stdout.strip():
        log_error("PostgreSQL pod not found; cannot create keycloak database.")
        return

    postgres_pod = result.stdout.strip()
    pg_password = os.environ.get("POSTGRES_PASSWORD", "")

    result = subprocess.run([
        "kubectl", "exec", "-n", "infra", postgres_pod, "--",
        "env", f"PGPASSWORD={pg_password}", "psql", "-U", "postgres", "-tAc",
        "SELECT 1 FROM pg_database WHERE datname='keycloak';"
    ], capture_output=True, text=True)

    if result.stdout.strip() == "1":
        log_info("Keycloak database already exists.")
        return

    subprocess.run([
        "kubectl", "exec", "-n", "infra", postgres_pod, "--",
        "env", f"PGPASSWORD={pg_password}", "psql", "-U", "postgres", "-c",
        "CREATE DATABASE keycloak;"
    ], check=True)
    log_info("Keycloak database created.")


def apply_root_app():
    """Apply root application to trigger ArgoCD sync."""
    log_info("Applying root-app.yaml to trigger ArgoCD sync...")
    root_app = REPO_ROOT / "boostrap" / "root-app.yaml"

    if not root_app.exists():
        log_error(f"root-app.yaml not found at {root_app}")
        sys.exit(1)

    subprocess.run(["kubectl", "apply", "-f", str(root_app)], check=True)
    patch_traefik_templates()
    log_info("Root Application applied.")


def render_template(template_path: Path) -> str:
    """Render a template file with environment variables."""
    import re
    content = template_path.read_text()
    content = content.replace('\r', '')

    def substitute(match):
        key = match.group(1)
        return os.environ.get(key, match.group(0))

    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", substitute, content)


def patch_traefik_templates():
    """Apply Traefik templates with user email."""
    if not os.environ.get("TRAEFIK_EMAIL"):
        log_warn("TRAEFIK_EMAIL not configured; skipping Traefik template rendering.")
        return

    template_dir = REPO_ROOT / "infra" / "services" / "gateway"
    log_info("Applying user-specific Traefik configuration from prompted email...")
    traefik_config = template_dir / "traefik-config.yaml"
    traefik_acme = template_dir / "traefik-acme-secret.yaml"

    if traefik_config.exists():
        rendered = render_template(traefik_config)
        subprocess.run(["kubectl", "apply", "-f", "-"], input=rendered.encode())
    if traefik_acme.exists():
        rendered = render_template(traefik_acme)
        subprocess.run(["kubectl", "apply", "-f", "-"], input=rendered.encode())

    log_info("Traefik email applied to kube-system resources.")


def wait_for_keycloak():
    """Wait for Keycloak to be ready."""
    log_info("Waiting for Keycloak to be ready...")
    elapsed = 0
    while elapsed < KEYCLOAK_TIMEOUT:
        result = subprocess.run([
            "kubectl", "get", "pods", "-n", "infra", "-l", "app=keycloak",
            "-o", "jsonpath={.items[0].status.conditions[?(@.type==\"Ready\")].status}"
        ], capture_output=True, text=True)

        if result.stdout.strip() == "True":
            log_info("Keycloak is ready!")
            return

        print(".", end="", flush=True)
        time.sleep(10)
        elapsed += 10

    print()
    log_error("Timeout waiting for Keycloak to be ready.")
    sys.exit(1)


def get_keycloak_pod() -> Optional[str]:
    """Get Keycloak pod name."""
    result = subprocess.run([
        "kubectl", "get", "pods", "-n", "infra", "-l", "app=keycloak",
        "-o", "jsonpath={.items[0].metadata.name}"
    ], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def kubectl_exec(namespace: str, pod: str, command: str) -> str:
    """Execute command in a pod."""
    result = subprocess.run([
        "kubectl", "exec", "-n", namespace, pod, "--", "bash", "-c", command
    ], capture_output=True, text=True)
    return result.stdout.strip()


def create_keycloak_infra_realm():
    """Create Keycloak infra realm."""
    log_info("=== Creating Keycloak infra Realm ===")

    keycloak_pod = get_keycloak_pod()
    if not keycloak_pod:
        log_error("Keycloak pod not found")
        return

    keycloak_url = "http://keycloak.infra.svc.cluster.local:8080"

    log_info("Waiting for Keycloak API to be ready...")
    api_ready = False
    for _ in range(30):
        result = subprocess.run([
            "kubectl", "exec", "-n", "infra", keycloak_pod, "--",
            "curl", "-sf", f"{keycloak_url}/health/ready"
        ], capture_output=True)
        if result.returncode == 0:
            api_ready = True
            break
        time.sleep(2)

    if not api_ready:
        for _ in range(30):
            result = subprocess.run([
                "kubectl", "exec", "-n", "infra", keycloak_pod, "--",
                "curl", "-sf", f"{keycloak_url}/realms/{KEYCLOAK_REALM}"
            ], capture_output=True)
            if result.returncode == 0:
                api_ready = True
                break
            time.sleep(2)

    log_info(f"Creating {KEYCLOAK_REALM} realm...")

    kc_script = f"""
export KEYCLOAK_HOME='/opt/bitnami/keycloak'
export PATH="$KEYCLOAK_HOME/bin:$PATH"
REALM='{KEYCLOAK_REALM}'

kcadm.sh config credentials --server '{keycloak_url}' --realm master --user admin --password '{os.environ.get('KEYCLOAK_ADMIN_PASSWORD', '')}' || exit 1

if kcadm.sh get realms/$REALM &> /dev/null; then
    echo "$REALM realm already exists"
else
    kcadm.sh create realms -s realm=$REALM -s enabled=true -s loginWithEmailAllowed=false -s duplicateEmailsAllowed=true -s resetPasswordAllowed=false
    echo "$REALM realm created"
fi
"""
    kubectl_exec("infra", keycloak_pod, kc_script)

    log_info(f"Creating {KEYCLOAK_REALM} realm clients...")

    grafana_uri = f"https://{ROUTE_GRAFANA}.{CLUSTER_DOMAIN}"
    argocd_uri = f"https://{ROUTE_ARGOCD}.{CLUSTER_DOMAIN}"
    headlamp_uri = f"https://{ROUTE_HEADLAMP}.{CLUSTER_DOMAIN}"

    clients_script = f"""
export KEYCLOAK_HOME='/opt/bitnami/keycloak'
export PATH="$KEYCLOAK_HOME/bin:$PATH"
REALM='{KEYCLOAK_REALM}'

kcadm.sh config credentials --server '{keycloak_url}' --realm master --user admin --password '{os.environ.get('KEYCLOAK_ADMIN_PASSWORD', '')}' || exit 1

echo 'Creating k3s-api client...'
kcadm.sh create clients -r '$REALM' -s clientId=k3s-api -s enabled=true -s protocol=openid-connect -s publicClient=false -s serviceAccountsEnabled=true -s standardFlowEnabled=false -s directAccessGrantsEnabled=true

echo 'Creating Grafana client...'
kcadm.sh create clients -r '$REALM' -s clientId=$REALM-grafana -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s 'redirectUris=["http://localhost:3000/*","http://grafana.infra.svc.cluster.local:3000/*"]' -s webOrigins='["+"]' -s serviceAccountsEnabled=true || true

echo 'Creating ArgoCD client...'
kcadm.sh create clients -r '$REALM' -s clientId=$REALM-argocd -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s 'redirectUris=["http://localhost:8080/*","http://argocd-server.argocd.svc.cluster.local:8080/*"]' -s webOrigins='["+"]' -s serviceAccountsEnabled=true || true

echo 'Creating Headlamp client...'
kcadm.sh create clients -r '$REALM' -s clientId=$REALM-headlamp -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s 'redirectUris=["http://localhost:4466/*","http://headlamp.infra.svc.cluster.local/*"]' -s webOrigins='["+"]' -s serviceAccountsEnabled=true || true

echo "$REALM clients created"
"""
    kubectl_exec("infra", keycloak_pod, clients_script)
    log_info(f" {KEYCLOAK_REALM} realm setup complete.")


def configure_k3s_oidc():
    """Configure K3s OIDC with Keycloak."""
    log_info("=== Configuring K3s OIDC with Keycloak ===")

    k3s_config_dir = Path("/etc/rancher/k3s")
    k3s_config_dir.mkdir(parents=True, exist_ok=True)

    config_content = f"""kube-apiserver-arg:
  - oidc-issuer-url:https://keycloak.cluster.local/realms/{KEYCLOAK_REALM}
  - oidc-username-claim:preferred_username
  - oidc-groups-claim:groups
  - oidc-client-id:k3s-api
"""
    config_file = k3s_config_dir / "k3s_server.yaml"
    config_file.write_text(config_content)

    # Replace cluster domain
    content = config_file.read_text().replace("keycloak.cluster.local", os.environ.get("CLUSTER_DOMAIN", "cluster.local"))
    config_file.write_text(content)

    log_info(f"K3s OIDC config written to {config_file}")
    log_info("Restart K3s to apply: sudo systemctl restart k3s")


def configure_keycloak_clients():
    """Configure Keycloak clients and update secrets."""
    log_info("=== Configuring Keycloak Clients ===")

    keycloak_pod = get_keycloak_pod()
    if not keycloak_pod:
        log_error("Keycloak pod not found")
        return

    keycloak_url = "http://keycloak.infra.svc.cluster.local:8080"
    realm = KEYCLOAK_REALM

    # Wait for API
    log_info("Waiting for Keycloak API to be ready...")
    api_ready = False
    for _ in range(30):
        result = subprocess.run([
            "kubectl", "exec", "-n", "infra", keycloak_pod, "--",
            "curl", "-sf", f"{keycloak_url}/health/ready"
        ], capture_output=True)
        if result.returncode == 0:
            api_ready = True
            break
        time.sleep(2)

    if not api_ready:
        log_warn("Keycloak API not ready yet, using alternative endpoint check...")
        for _ in range(30):
            result = subprocess.run([
                "kubectl", "exec", "-n", "infra", keycloak_pod, "--",
                "curl", "-sf", f"{keycloak_url}/realms/{realm}"
            ], capture_output=True)
            if result.returncode == 0:
                api_ready = True
                break
            time.sleep(2)

    # Setup realm if not exists
    log_info("Creating Keycloak realm if not exists...")
    realm_script = f"""
export KEYCLOAK_HOME='/opt/bitnami/keycloak'
export PATH="$KEYCLOAK_HOME/bin:$PATH"

kcadm.sh config credentials --server '{keycloak_url}' --realm master --user admin --password '{os.environ.get('KEYCLOAK_ADMIN_PASSWORD', '')}'

echo 'Checking if realm {realm} exists...'
if ! kcadm.sh get realms/{realm} &>/dev/null; then
    echo 'Creating realm {realm}...'
    kcadm.sh create realms -s realm={realm} -s enabled=true -s loginWithEmailAllowed=false -s duplicateEmailsAllowed=true -s resetPasswordAllowed=false
else
    echo 'Realm {realm} already exists'
fi
"""
    kubectl_exec("infra", keycloak_pod, realm_script)

    # Create clients
    log_info("Creating Keycloak clients using kcadm...")
    clients_script = f"""
export KEYCLOAK_HOME='/opt/bitnami/keycloak'
export PATH="$KEYCLOAK_HOME/bin:$PATH"

kcadm.sh config credentials --server '{keycloak_url}' --realm master --user admin --password '{os.environ.get('KEYCLOAK_ADMIN_PASSWORD', '')}'

echo 'Creating Grafana client...'
kcadm.sh create clients -r '{realm}' -s clientId={realm}-grafana -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s 'redirectUris=["http://localhost:3000/*","http://grafana.infra.svc.cluster.local:3000/*"]' -s webOrigins='["+"]' -s serviceAccountsEnabled=true || true

echo 'Creating ArgoCD client...'
kcadm.sh create clients -r '{realm}' -s clientId={realm}-argocd -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s 'redirectUris=["http://localhost:8080/*","http://argocd-server.argocd.svc.cluster.local:8080/*"]' -s webOrigins='["+"]' -s serviceAccountsEnabled=true || true

echo 'Creating Headlamp client...'
kcadm.sh create clients -r '{realm}' -s clientId={realm}-headlamp -s enabled=true -s protocol=openid-connect -s publicClient=false -s standardFlowEnabled=true -s 'redirectUris=["http://localhost:4466/*","http://headlamp.infra.svc.cluster.local/*"]' -s webOrigins='["+"]' -s serviceAccountsEnabled=true || true
"""
    kubectl_exec("infra", keycloak_pod, clients_script)

    # Get client secrets
    log_info("Retrieving client secrets from Keycloak...")

    def get_client_secret(client_id: str) -> str:
        script = f"""
export KEYCLOAK_HOME='/opt/bitnami/keycloak'
export PATH="$KEYCLOAK_HOME/bin:$PATH"

kcadm.sh config credentials --server '{keycloak_url}' --realm master --user admin --password '{os.environ.get('KEYCLOAK_ADMIN_PASSWORD', '')}'
CID=$(kcadm.sh get clients -r '{realm}' -q clientId={client_id} --fields id 2>/dev/null | grep '"id"' | head -1 | sed 's/.*: *"//;s/".*//')
if [ -n "$CID" ]; then
    kcadm.sh get clients/$CID/client-secret -r '{realm}' 2>/dev/null | grep '"value"' | sed 's/.*: *"//;s/".*//'
fi
"""
        result = kubectl_exec("infra", keycloak_pod, script)
        return result.replace('\r', '').replace('\n', '')

    grafana_secret = get_client_secret(f"{realm}-grafana")
    argocd_secret = get_client_secret(f"{realm}-argocd")
    headlamp_secret = get_client_secret(f"{realm}-headlamp")

    # Update Grafana secret
    if grafana_secret and grafana_secret != "null":
        cmd = ["kubectl", "create", "secret", "generic", "grafana-secret", "-n", "infra",
               f"--from-literal=admin-password={os.environ.get('GRAFANA_ADMIN_PASSWORD', '')}",
               f"--from-literal=oidc-client-secret={grafana_secret}"]
        result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
        subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())
        log_info("Grafana secret updated with Keycloak client secret.")
    else:
        log_warn("Could not retrieve Grafana client secret.")

    if argocd_secret and argocd_secret != "null":
        log_info("ArgoCD client secret retrieved.")
    else:
        log_warn("Could not retrieve ArgoCD client secret.")

    if headlamp_secret and headlamp_secret != "null":
        cmd = ["kubectl", "create", "secret", "generic", "headlamp-oidc-secret", "-n", "infra",
               "--from-literal=OIDC_CLIENT_ID=headlamp",
               f"--from-literal=OIDC_CLIENT_SECRET={headlamp_secret}",
               f"--from-literal=OIDC_ISSUER_URL={keycloak_url}/realms/{realm}"]
        result = subprocess.run(cmd + ["--dry-run=client", "-o", "yaml"], capture_output=True, text=True)
        subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout.encode())
        log_info("Headlamp OIDC secret created with Keycloak credentials.")
    else:
        log_warn("Could not retrieve Headlamp client secret.")

    log_info("Keycloak clients configured.")
    ensure_keycloak_dns_alias()


def ensure_keycloak_dns_alias():
    """Add Keycloak DNS alias to CoreDNS."""
    alias_domain = f"auth.{os.environ.get('CLUSTER_DOMAIN', 'cluster.local')}"
    alias_line = f"{os.environ.get('KEYCLOAK_HOST_IP', '')} {alias_domain}"
    nodehosts = Path("/etc/coredns/NodeHosts")

    if not os.environ.get("KEYCLOAK_HOST_IP"):
        log_error("cluster.hostIP is not configured in config.yaml. Set the alias IP before touching CoreDNS hosts.")
        sys.exit(1)

    if not nodehosts.exists():
        log_warn(f"{nodehosts} not found; creating placeholder file.")
        try:
            nodehosts.write_text("")
        except Exception:
            pass

    if nodehosts.exists():
        content = nodehosts.read_text()
        if alias_line in content:
            log_info(f"Keycloak auth alias already present in {nodehosts}.")
        else:
            log_info(f"Adding Keycloak auth alias to {nodehosts}.")
            with open(nodehosts, "a") as f:
                f.write(f"{alias_line}\n")

    log_info("Restarting CoreDNS so it picks up the alias.")
    result = subprocess.run([
        "kubectl", "-n", "kube-system", "rollout", "restart", "deployment/coredns"
    ], capture_output=True)
    if result.returncode == 0:
        log_info("CoreDNS restart triggered.")
    else:
        log_warn("CoreDNS restart failed; check kubeconfig/permissions.")

    check_dns_forwarders()


def prompt_grafana_password():
    """Prompt for Grafana admin password."""
    password = prompt_secret("Grafana Admin Password", "GRAFANA_ADMIN_PASSWORD", "Enter Grafana admin password")
    os.environ["GRAFANA_ADMIN_PASSWORD"] = password


def poll_applications():
    """Poll for application health."""
    log_info("Polling for application health...")

    elapsed = 0
    while elapsed < HEALTH_CHECK_TIMEOUT:
        result = subprocess.run([
            "kubectl", "get", "applications", "-n", "argocd",
            "-o", "jsonpath={range .items[?(@.status.health.status!=\"Healthy\")]} {.metadata.name}{\"\\n\"}{end}"
        ], capture_output=True, text=True)

        unhealthy = result.stdout.strip()

        if not unhealthy:
            result = subprocess.run([
                "kubectl", "get", "applications", "-n", "argocd", "-o", "name"
            ], capture_output=True, text=True)
            all_apps = len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0
            if all_apps > 0:
                log_info("All applications are healthy!")
                return True

        print(".", end="", flush=True)
        time.sleep(HEALTH_CHECK_INTERVAL)
        elapsed += HEALTH_CHECK_INTERVAL

    print()
    log_error("Timeout waiting for applications to become healthy.")
    log_warn("Current application status:")
    subprocess.run(["kubectl", "get", "applications", "-n", "argocd"])
    return False


def main():
    log_info("=== K8s Cluster Bootstrap Script ===")
    log_info("This script will install K3s, collect secrets, install ArgoCD, configure Keycloak, and verify service health.")
    print()

    check_requirements()
    load_config()
    load_env_file()
    require_config_update()

    install_k3s()
    print()

    prompt_secrets()
    print()

    create_secrets()
    print()

    reset_existing_argocd()
    install_argocd()
    install_argocd_cli()
    print()

    apply_root_app()
    create_keycloak_database()
    print()

    log_info("Waiting for base services (PostgreSQL, Redis, Keycloak) to be ready...")
    time.sleep(30)

    wait_for_keycloak()
    print()

    create_keycloak_infra_realm()
    print()

    configure_k3s_oidc()
    print()

    prompt_grafana_password()
    print()

    configure_keycloak_clients()
    print()

    if poll_applications():
        log_info("=== Bootstrap Complete ===")
        log_info("All services are healthy!")
        log_info("ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:8080")
        log_info("Keycloak: kubectl port-forward svc/keycloak -n infra 8080:8080")
        log_info("Headlamp: kubectl port-forward svc/headlamp -n infra 4466:80")
        log_info("  (Login with: kubectl create token headlamp -n infra)")
        sys.exit(0)
    else:
        log_error("=== Bootstrap Failed ===")
        log_error("Some services did not become healthy within timeout.")
        sys.exit(1)


if __name__ == "__main__":
    main()
