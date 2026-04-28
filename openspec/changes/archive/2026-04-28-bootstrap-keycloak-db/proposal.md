## Why

Keycloak fails to authenticate because the `keycloak` database is not created ahead of time, and bootstrapping currently relies on a manual `psql` command every time. Embedding that step into the bootstrap automation prevents `password authentication failed` errors and ensures the Pod can mount the database password secret safely.

## What Changes

- Extend `scripts/run-all.sh` to wait for PostgreSQL, create the `postgres-secret`, and create the `keycloak` database when bootstrapping locally so Keycloak comes up without manual intervention.
- Introduce a new helper in `infra/services/iam/keycloak` or documentation that expresses the expectation that the database already exists once ArgoCD syncs the Keycloak manifests.
- Document the new bootstrap behavior in `README.md` so operators understand the database creation now happens automatically.

## Capabilities

### New Capabilities
- `bootstrap-keycloak-db`: Automate PostgreSQL readiness checks and the `keycloak` database creation during bootstrap so the service can start reliably with the shared credentials.

### Modified Capabilities
- `- None.`

## Impact

- `scripts/run-all.sh` (new helper logic and `kubectl exec` commands)
- `infra/services/iam/keycloak` (documentation and expectation in the README or in-file notes)
- `README.md` (document the bootstrap step and the database dependency)

## Non-goals

- Adding additional PostgreSQL users or service accounts beyond the existing `postgres` service account.
- Running this database creation in production clusters where a managed database is provided externally.
