## 1. Manifest & secrets

- [x] 1.1 Update `infra/services/iam/keycloak/keycloak-deployment.yaml` so the container uses `KC_BOOTSTRAP_ADMIN_USERNAME`/`KC_BOOTSTRAP_ADMIN_PASSWORD` (sourced from `keycloak-secret`) and drop the old `KEYCLOAK_ADMIN_*` vars.
- [x] 1.2 Ensure `scripts/run-all.sh` populates `keycloak-secret` with `KC_BOOTSTRAP_ADMIN_USERNAME` and `KC_BOOTSTRAP_ADMIN_PASSWORD` so automation supplies the new keys.

## 2. Validation & communication

- [x] 2.1 Run `kubectl apply --dry-run=client -f infra/services/iam/keycloak/keycloak-deployment.yaml` to verify the manifest.
- [x] 2.2 Update `README.md` to mention the KC bootstrap var names and document the change in the recent updates list.
