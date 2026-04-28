## 1. Manifest alignment

- [x] 1.1 Update `infra/services/iam/keycloak/keycloak-deployment.yaml` so the container sets `KEYCLOAK_BOOTSTRAP_ADMIN_USERNAME` and `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` (sourced from `keycloak-secret`) instead of the legacy admin env vars.
- [x] 1.2 Confirm the service definition continues to expose port 8080/8443 and needs no further changes.

## 2. Validation & documentation

- [x] 2.1 Run `kubectl apply --dry-run=client -f infra/services/iam/keycloak/keycloak-deployment.yaml` to validate the updated manifest.
- [x] 2.2 Document the required secret keys and env var names in `README.md` so future maintainers know what the deployment expects.
