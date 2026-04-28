## 1. Credential alignment

- [x] 1.1 Update `scripts/run-all.sh` so the Keycloak secret copies `POSTGRES_PASSWORD` into the bootstrap password entries and drops the separate Keycloak database password prompt.
- [x] 1.2 Adjust `infra/services/iam/keycloak/keycloak-deployment.yaml` to read `KEYCLOAK_DATABASE_PASSWORD` from `postgres-secret` instead of `keycloak-secret`.

## 2. Validation & documentation

- [x] 2.1 Run `kubectl apply --dry-run=client -f infra/services/iam/keycloak/keycloak-deployment.yaml` to validate the new env configuration.
- [x] 2.2 Update `README.md` so the secrets table and secrets export instructions describe that Keycloak uses the Postgres password, and note the change in the recent updates log.
