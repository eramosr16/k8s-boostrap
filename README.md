# K8s Cluster Manifests

This repository defines a Kubernetes cluster deployed via ArgoCD using the App-of-Apps pattern. It separates **services** (core infrastructure like databases, caching, message brokers) from **applications** (end-user interfaces and gateways).

## Folder Structure

```
cluster-bootstrap/
├── bootstrap/
│   └── root-app.yaml           # Watches the /infra folder
└── infra/
    ├── services/               # Low-level platform services
    │   ├── databases/
    │   │   ├── postgres/
    │   │   └── redis/
    │   ├── gateway/
    │   │   ├── traefik.yaml
    │   │   ├── cert-manager.yaml
    │   │   └── external-dns.yaml
    │   ├── broker/
    │   │   └── rabbitmq/
    │   ├── iam/
    │   │   └── keycloak/
    │   └── observability/
    │       ├── prometheus/
    │       ├── grafana/
    │       ├── loki/
    │       ├── seq/
    │       ├── opentelemetry/
    │       └── headlamp/
    │
    └── applications/           # End-user applications
```

## Directory Reference

| Directory             | Description                                                             |
| --------------------- | ----------------------------------------------------------------------- |
| `infra/services/`     | Core infrastructure (databases, caching, messaging, IAM, observability) |
| `infra/applications/` | User-facing applications deployed on top of services                    |

## Repository URL Configuration

The `bootstrap/root-app.yaml` file uses `repoURL` to specify where ArgoCD should pull manifests from. Update this value based on your deployment environment:

### Local Testing

```yaml
repoURL: file:///home/ernesto/Repository/Cluster/k8s
```

### Remote Git Repository

```yaml
repoURL: https://github.com/<your-username>/k8s.git
# Or for SSH
repoURL: git@github.com:<your-username>/k8s.git
```

### Local Git Server

```yaml
repoURL: http://localhost:8080/k8s.git
```

## Quick Start - Automated Bootstrap

The easiest way to set up the cluster is using the automated `run-all.sh` script. It installs K3s, ArgoCD, prompts for all credentials, creates secrets, configures Keycloak clients, and verifies service health.

### Prerequisites

- Linux host (Ubuntu, Debian, CentOS, etc.)
- Root/sudo access
- Internet connection
- Git clone of this repository

### One-Command Setup

```bash
./scripts/run-all.sh
```

The script will prompt you for credentials (passwords are hidden for security):

1. **PostgreSQL** - Database password
2. **Redis** - Cache password
3. **RabbitMQ** - Username and password
4. **Keycloak** - Admin password and database password
5. **Seq** - Admin password
6. **Let's Encrypt** - Email for TLS certificates
7. **AWS** (optional) - Access key and secret for ECR

### What the Script Does

1. **Installs K3s** - Creates Kubernetes cluster
2. **Installs ArgoCD** - GitOps deployment tool
3. **Prompts for credentials** - Secure input for all service passwords
4. **Creates Kubernetes secrets** - Stores credentials in `infra` namespace
5. **Applies root-app.yaml** - Triggers ArgoCD to deploy all services
6. **Configures Keycloak clients** - Creates OIDC clients for Grafana and ArgoCD automatically
7. **Polls for health** - Waits until all services are healthy (timeout: 5 minutes)

### Accessing Services

After successful bootstrap:

```bash
# ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open http://localhost:8080 - Username: admin

# Keycloak Admin Console
kubectl port-forward svc/keycloak -n infra 8080:8080
# Open http://localhost:8080 - Username: admin

# Headlamp
kubectl port-forward svc/headlamp -n infra 4466:80
# Open http://localhost:4466 - Use service account token

# Grafana
kubectl port-forward svc/grafana -n infra 3000:3000
# Open http://localhost:3000
```

### Quick Start - Manual Setup

If you prefer to set up manually (or need more control), follow these steps:

#### Prerequisites

- Linux host (Ubuntu, Debian, CentOS, etc.)
- Root/sudo access
- Internet connection

#### Installation

1. **Install K3s** (creates Kubernetes cluster):

   ```bash
   ./scripts/bootstrap.sh
   ```

2. **Install ArgoCD** (GitOps deployment tool):

   ```bash
   ./scripts/install-argocd.sh
   ```

3. **Access ArgoCD UI**:

   ```bash
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   ```

   Then open http://localhost:8080 in your browser.
   - **Username**: `admin`
   - **Password**: Use the password shown during installation

#### Notes

- Both scripts are idempotent - safe to run multiple times
- K3s data is at `/var/lib/rancher/k3s`
- To uninstall K3s: `curl -sfL https://get.k3s.io | sh -s - --uninstall`

## Traefik Configuration

K3s ships with Traefik as the default ingress controller. This repo includes manifests for TLS certificate management.

### Let's Encrypt Setup

The Traefik manifests use an email placeholder for Let's Encrypt. Before deploying:

1. Edit `infra/services/gateway/traefik-acme-secret.yaml`
2. Replace `LETS_ENCRYPT_EMAIL` with your actual email address

```yaml
stringData:
  email: "admin@example.com" # Replace with your email
```

### Middlewares Available

- `redirect-http-to-https` - Redirects HTTP to HTTPS
- `security-headers` - Adds security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- `rate-limit` - Rate limiting (100 req/s average, 50 burst)

## Service Connection Details

Internal service endpoints accessible within the cluster:

| Service       | DNS Name                                          | Port | Namespace |
| ------------- | ------------------------------------------------- | ---- | --------- |
| PostgreSQL    | `postgres.infra.svc.cluster.local`                | 5432 | infra     |
| Redis         | `redis.infra.svc.cluster.local`                   | 6379 | infra     |
| RabbitMQ      | `rabbitmq.infra.svc.cluster.local`                | 5672 | infra     |
| Prometheus    | `prometheus.infra.svc.cluster.local`              | 9090 | infra     |
| Grafana       | `grafana.infra.svc.cluster.local`                 | 3000 | infra     |
| Keycloak      | `keycloak.infra.svc.cluster.local`                | 8080 | infra     |
| ArgoCD        | `argocd.infra.svc.cluster.local`                  | 443  | argocd    |
| OpenTelemetry | `opentelemetry-collector.infra.svc.cluster.local` | 4317 | infra     |
| Seq           | `seq.infra.svc.cluster.local`                     | 5341 | infra     |
| Headlamp      | `headlamp.infra.svc.cluster.local`                | 80   | infra     |

### Connection Examples

**PostgreSQL:**

```bash
# From another pod in the cluster
psql -h postgres.infra.svc.cluster.local -p 5432 -U postgres -d postgres
```

**Redis:**

```bash
# From another pod in the cluster
redis-cli -h redis.infra.svc.cluster.local -p 6379
```

**RabbitMQ:**

```bash
# From another pod in the cluster
# AMQP port 5672, Management UI at 15672
amqp-connect -h rabbitmq.infra.svc.cluster.local -p 5672
```

**Prometheus (internal):**

```bash
# From another pod in the cluster
curl http://prometheus.infra.svc.cluster.local:9090
```

**Grafana (internal):**

```bash
# From another pod in the cluster
curl http://grafana.infra.svc.cluster.local:3000
```

**Keycloak (internal):**

```bash
# From another pod in the cluster
curl http://keycloak.infra.svc.cluster.local:8080
```

### Notes

- Both PostgreSQL and Redis are configured with ClusterIP services (internal only)
- Secrets are stored in `infra` namespace - update passwords before production use
- Storage is persistent via PersistentVolumeClaim

## Managing Secrets

Secrets use environment variable placeholders that are replaced during deployment:

| Service    | Secret File          | Environment Variable                                    |
| ---------- | -------------------- | ------------------------------------------------------- |
| PostgreSQL | postgres-secret.yaml | `POSTGRES_PASSWORD`                                     |
| Redis      | redis-secret.yaml    | `REDIS_PASSWORD`                                        |
| RabbitMQ   | rabbitmq-secret.yaml | `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`        |
| Prometheus | -                    | -                                                       |
| Grafana    | grafana-secret.yaml  | `GRAFANA_OIDC_CLIENT_SECRET`, `GRAFANA_ADMIN_PASSWORD`  |
| Keycloak   | keycloak-secret.yaml | `KEYCLOAK_ADMIN_PASSWORD`, `KEYCLOAK_DATABASE_PASSWORD` |
| Seq        | seq-secret.yaml      | `SEQ_ADMIN_PASSWORD`                                    |
| Headlamp   | -                    | - (uses service account token)                          |

### Setting Passwords

Before deploying, set the password by exporting the environment variable:

```bash
# For PostgreSQL
export POSTGRES_PASSWORD="your-secure-password"

# For Redis
export REDIS_PASSWORD="your-secure-password"

# For RabbitMQ
export RABBITMQ_DEFAULT_USER="your-secure-user"
export RABBITMQ_DEFAULT_PASS="your-secure-password"

# For Grafana
export GRAFANA_OIDC_CLIENT_SECRET="your-secure-client-secret"
export GRAFANA_ADMIN_PASSWORD="your-secure-password"

# For Keycloak
export KEYCLOAK_ADMIN_PASSWORD="your-secure-password"
export KEYCLOAK_DATABASE_PASSWORD="your-secure-password"
```

Then update the secret file with the actual password or use a tool like `envsubst` to replace the placeholder during deployment.

## Pre-Deployment Checklist

Before deploying services, ensure the following are configured:

- [ ] **DNS**: `auth.mydomain.com`, `argocd.mydomain.com`, `metrics.mydomain.com`, `logs.mydomain.com`, and `headlamp.mydomain.com` point to your cluster's external IP
- [ ] **Let's Encrypt**: Email configured in `traefik-acme-secret.yaml`
- [ ] **Secrets**: All passwords set in respective secret files
- [ ] **Keycloak Client**: Grafana and ArgoCD OIDC clients configured in Keycloak master realm
- [ ] **PostgreSQL**: Running and accessible before deploying Keycloak
- [ ] **Prometheus**: Running before deploying Grafana (for datasource)

## Keycloak Configuration

All services that use Keycloak for authentication (Grafana, ArgoCD, etc.) are configured to use the **master realm**.

### Existing Clients

- **Grafana**: OIDC client for Grafana authentication
- **ArgoCD**: OIDC client for ArgoCD authentication (PKCE enabled)

### Groups

Create the following groups in the master realm:

- `argocd-admins` - Users in this group get admin access to ArgoCD
- `grafana-admins` - Users in this group get admin access to Grafana
- `grafana-editors` - Users in this group get editor access to Grafana

### ArgoCD Keycloak Client Setup

1. Create a new client in Keycloak (master realm)
2. Client ID: `argocd`
3. Client Protocol: `openid-connect`
4. **Disable** Client Authentication (use PKCE)
5. Valid Redirect URIs: `https://argocd.mydomain.com/auth/callback`
6. Web Origins: `https://argocd.mydomain.com`
7. Add client scope for groups with Token Mapper (Group Membership)
8. Create `argocd-admins` group and add admin users
