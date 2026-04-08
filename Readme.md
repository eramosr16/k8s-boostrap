# Description

The purpose of this project is to set the blue print for a setup of a K8s cluster with the basic services that you need to host applications, the idea is to utilize ArgoCD as main orchestrator and deployer/configuration and handling of the basic services layer(tls, databases, caching, message broker, logs and metrics handling) and the application layer.
To strictly separate services (the core logic/databases) from applications (the end-user interfaces or gateways) while adhering to the App-of-Apps pattern you linked, we should categorize them into sub-folders within your apps/ directory.


cluster-bootstrap/
├── bootstrap/
│   └── root-app.yaml           # Watches the /infra folder
└── infra/
    ├── services/         # Low-level platform services
    │   ├── databases/postgres.yaml       # Database service
    │   ├── databases/redis.yaml          # Caching service
    │   ├── gateway/traefik.yaml        # Ingress controller
    │   ├── gateway/cert-manager.yaml   # SSL management
    │   ├── gateway/external-dns.yaml
    │   ├── broker/rabbitmq.yaml
        ├── iam/keycloak.yaml
    │   ├── observability/prometheus.yaml          
    │   └── observability/opentelemetry.yaml      
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
    