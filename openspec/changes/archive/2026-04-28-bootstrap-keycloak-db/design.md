## Context

- The Keycloak deployment mounts the `postgres-secret` and expects a `keycloak` database to already exist, but bootstrap today requires a manual `psql` command after the cluster is up.
- This manual step is brittle in automation, which means new clusters often see Keycloak fail with `password authentication failed for user "postgres"` as soon as the pod tries to connect.
- Since `scripts/run-all.sh` already prompts for `POSTGRES_PASSWORD` and creates the secrets, it is the natural place to also ensure the `keycloak` database is created before Keycloak starts.

## Goals / Non-Goals

**Goals:**

- Extend bootstrap automation to wait for PostgreSQL readiness, create the `keycloak` database if missing, and log progress so operators can rely on a single script run.
- Keep the existing instructions for secrets and database user names but document that Keycloak reuses the Postgres credentials as part of this process.

**Non-Goals:**

- Creating separate Postgres clusters or replacing the existing StatefulSet with an external managed database.
- Changing Keycloak’s data model or migrations beyond ensuring the database exists.

## Decisions

- Implement the database creation inside `scripts/run-all.sh` after the Postgres Secret is created because all secrets and cluster context are already available there and we need the password to connect.
- Use `kubectl exec` against the Postgres pod to run `psql` and check for the database’s existence before running `CREATE DATABASE` to ensure idempotency.
- Document the automation in `README.md` so the expectation (Postgres provides the `keycloak` DB) is explicit and maintainers know why the script now executes SQL.

## Risks / Trade-offs

- [Timing] Waiting for Postgres to be ready may add startup time; mitigate by waiting only after secret creation and logging progress so operators understand the extra steps.
- [Permissions] The bootstrap script assumes the `postgres` user can create a new database; if this user is restricted in future, the script will fail and will need updating.

## Migration Plan

1. After `create_secrets`, wait for the Postgres pod to be ready and run a query that creates the `keycloak` database only if it does not already exist.
2. Keep the rest of the bootstrap steps unchanged so subsequent Keycloak and ArgoCD workloads see the new database automatically.
3. Update `README.md` to mention that `keycloak` is created during bootstrap and references the new script behavior.

## Open Questions

- Do we want to expose a toggle so production environments with managed databases can skip this creation step?
