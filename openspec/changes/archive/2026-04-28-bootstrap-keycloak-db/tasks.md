## 1. Bootstrap implementation

- [x] 1.1 Extend `scripts/run-all.sh` to wait for the Postgres pod, check for the `keycloak` database via `psql`, and create it if missing right after secrets are created.
- [x] 1.2 Ensure the Keycloak secret creation copies `POSTGRES_PASSWORD` into `KC_BOOTSTRAP_ADMIN_PASSWORD` so bootstrap credentials align with the database password.

## 2. Validation & documentation

- [x] 2.1 Run `kubectl exec -n infra postgres-0 -- psql ...` (via `--dry-run` or local verification) to confirm the creation command works and exit code stays zero when the DB already exists.
- [x] 2.2 Update `README.md` to describe the new bootstrap behavior and mention that the script now creates the `keycloak` database automatically.
