# Description

The purpose of this project is to set the blue print for a setup of a K8s cluster with the basic services that you need to host applications, the idea is to utilize ArgoCD as main orchestrator and deployer/configuration and handling of the basic services layer(tls, databases, caching, message broker, logs and metrics handling) and the application layer.
To strictly separate services (the core logic/databases) from applications (the end-user interfaces or gateways) while adhering to the App-of-Apps pattern you linked, we should categorize them into sub-folders within your apps/ directory.


cluster-bootstrap/
├── bootstrap/
│   └── root-app.yaml           # Watches the /infra folder
└── infra/
    ├── services/         # Low-level platform services
    │   ├── databases/postgres/       # Database service
    │   ├── databases/redis/          # Caching service
    │   ├── gateway/traefik.yaml        # Ingress controller
    │   ├── gateway/cert-manager.yaml   # SSL management
    │   ├── gateway/external-dns.yaml
    │   ├── broker/rabbitmq.yaml
    │   ├── iam/keycloak/           # Identity & access management
    │   ├── observability/prometheus.yaml        
    |   ├── observability/headlamp.yaml    
    |   ├── observability/seq.yaml    
    │   └── observability/opentelemetry.yaml      
    │
    ├── applications/          # State and persistent services
    │   ├── cert-manager.yaml   # SSL management
    │   └── external-dns.yaml
    │
    ├── applications/          # State and persistent services
    │   ├── cert-manager.yaml   # SSL management
    │   └── external-dns.yaml
    │

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

## Quick Start - Bootstrap Local Cluster

### Prerequisites
- Linux host (Ubuntu, Debian, CentOS, etc.)
- Root/sudo access
- Internet connection

### Installation

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

### Notes
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
  email: "admin@example.com"  # Replace with your email
```

### Middlewares Available

- `redirect-http-to-https` - Redirects HTTP to HTTPS
- `security-headers` - Adds security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- `rate-limit` - Rate limiting (100 req/s average, 50 burst)

## Service Connection Details

Internal service endpoints accessible within the cluster:

| Service   | DNS Name                              | Port | Namespace |
|-----------|---------------------------------------|------|-----------|
| PostgreSQL| `postgres.infra.svc.cluster.local`    | 5432 | infra     |
| Redis     | `redis.infra.svc.cluster.local`       | 6379 | infra     |
| RabbitMQ  | `rabbitmq.infra.svc.cluster.local`    | 5672 | infra     |
| Prometheus| `prometheus.infra.svc.cluster.local`  | 9090 | infra     |
| Grafana   | `grafana.infra.svc.cluster.local`     | 3000 | infra     |
| Keycloak | `keycloak.infra.svc.cluster.local`     | 8080 | infra     |
| ArgoCD    | `argocd.infra.svc.cluster.local`      | 443  | argocd    |
| OpenTelemetry | `opentelemetry-collector.infra.svc.cluster.local` | 4317 | infra |

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

| Service   | Secret File          | Environment Variable                            |
|-----------|---------------------|--------------------------------------------------|
| PostgreSQL| postgres-secret.yaml| `POSTGRES_PASSWORD`                              |
| Redis     | redis-secret.yaml   | `REDIS_PASSWORD`                                 |
| RabbitMQ  | rabbitmq-secret.yaml| `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS` |
| Prometheus| -                   | -                                                |
| Grafana   | grafana-secret.yaml | `GRAFANA_OIDC_CLIENT_SECRET`, `GRAFANA_ADMIN_PASSWORD` |
| Keycloak  | keycloak-secret.yaml| `KEYCLOAK_ADMIN_PASSWORD`, `KEYCLOAK_DATABASE_PASSWORD` |

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

- [ ] **DNS**: `auth.mydomain.com`, `argocd.mydomain.com` and `metrics.mydomain.com` point to your cluster's external IP
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
    