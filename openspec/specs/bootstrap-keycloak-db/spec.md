## ADDED Requirements

### Requirement: Bootstrap process creates Keycloak database
The bootstrap sequence SHALL wait for the Postgres pod to become ready and execute SQL that ensures the `keycloak` database exists before Keycloak is deployed.

#### Scenario: Idempotent database creation
- **WHEN** `scripts/run-all.sh` runs on a fresh cluster
- **THEN** the script waits for Postgres readiness, queries `pg_database`, and executes `CREATE DATABASE keycloak;` only if the database is missing, logging success before continuing.

### Requirement: Bootstrap script copies Postgres password for Keycloak
After collecting secrets, the bootstrap script SHALL set `KEYCLOAK_DATABASE_PASSWORD` and `KC_BOOTSTRAP_ADMIN_PASSWORD` to the same value as `POSTGRES_PASSWORD` so the Keycloak secrets and PostgreSQL credentials stay in sync.

#### Scenario: Secret alignment
- **WHEN** `scripts/run-all.sh` finishes `prompt_secrets` and `create_secrets`
- **THEN** the Keycloak secret stores `KC_BOOTSTRAP_ADMIN_PASSWORD=POSTGRES_PASSWORD` and Keycloak deployment reads `KP` from `postgres-secret`, so no manual password updates are required.
