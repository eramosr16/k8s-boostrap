## Why

Keycloak currently fails to start because it tries to connect to PostgreSQL with a password that does not match the value stored in `postgres-secret`. The deployment and bootstrap scripts ask for a separate Keycloak database password, but the database user is the same `postgres` service account that already uses `POSTGRES_PASSWORD`. Aligning these values prevents authentication failures and keeps secrets predictable.

## What Changes

- Drop the standalone Keycloak database password prompt and always use the same password that the PostgreSQL StatefulSet uses (`POSTGRES_PASSWORD`).
- Update `infra/services/iam/keycloak/keycloak-deployment.yaml` so the pod reads its database password from `postgres-secret` directly, guaranteeing the credentials match the database it connects to.
- Document the new expectation in `README.md` and the change log so operators know which secret holds Keycloak’s DB credentials.

## Capabilities

### New Capabilities
- `keycloak-db-creds-sync`: Ensure the Keycloak deployment, onboarding script, and docs all agree that `KEYCLOAK_DATABASE_PASSWORD` is the same as `POSTGRES_PASSWORD` so the optimized image can authenticate reliably.

### Modified Capabilities
- `- None.`

## Impact

- `infra/services/iam/keycloak/keycloak-deployment.yaml` (env configuration)
- `scripts/run-all.sh` (credential prompts and secret creation)
- `README.md` (secret reference table and changelog entry)
- Any automation that rotates the PostgreSQL password must continue to provide `POSTGRES_PASSWORD` since Keycloak now reuses it directly.

## Non-goals

- Supporting a separate Keycloak-only database password that diverges from Postgres credentials.
- Altering PostgreSQL user/account configuration beyond the default `postgres` service account.
