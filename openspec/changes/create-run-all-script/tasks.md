## 1. Script Structure

- [x] 1.1 Create `scripts/run-all.sh` with shebang and set -e
- [x] 1.2 Add function declarations (install_k3s, install_argocd, prompt_secrets, create_secrets, check_health)
- [x] 1.3 Add main execution flow

## 2. K3s and ArgoCD Installation

- [x] 2.1 Implement install_k3s function
- [x] 2.2 Implement install_argocd function
- [x] 2.3 Test both functions

## 3. Credential Prompts

- [x] 3.1 Implement prompt_secret function with secure input
- [x] 3.2 Add prompts for PostgreSQL, Redis, RabbitMQ, Grafana, Keycloak, Seq, Traefik ACME, AWS

## 4. Kubernetes Secret Creation

- [x] 4.1 Implement create_secrets function
- [x] 4.2 Create infra namespace if not exists
- [x] 4.3 Create each secret via kubectl

## 5. Health Check and Exit

- [x] 5.1 Apply root-app.yaml to trigger ArgoCD sync
- [x] 5.2 Implement poll_applications function with timeout
- [x] 5.3 Add proper exit codes (0 success, non-zero failure)
