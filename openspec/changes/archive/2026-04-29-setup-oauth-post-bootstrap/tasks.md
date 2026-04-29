## 1. Recovery script

- [x] 1.1 Create `scripts/setup-oauth-after-bootstrap.sh`, read the existing credential env vars, wait for Keycloak, and log progress.
- [x] 1.2 Implement the Keycloak kcadm flow inside the script so it ensures the `infra` realm, Grafana/ArgoCD/Headlamp clients, and their Kubernetes secrets are created or refreshed idempotently.

## 2. Docs and verification

- [x] 2.1 Document the recovery script in `README.md`, explaining when to run it and what environment variables are required.
- [x] 2.2 Describe how to verify Grafana, ArgoCD, and Headlamp can authenticate via Keycloak after running the script.
