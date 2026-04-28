## ADDED Requirements

### Requirement: Keycloak database password matches Postgres password
The Keycloak deployment SHALL source `KEYCLOAK_DATABASE_PASSWORD` directly from `postgres-secret`’s `POSTGRES_PASSWORD` so it always matches the credentials that the database enforces.

#### Scenario: Keycloak uses Postgres credentials
- **WHEN** the updated deployment is applied
- **THEN** Keycloak starts with `KEYCLOAK_DATABASE_PASSWORD` populated from `postgres-secret` and successfully opens a JDBC connection as the `postgres` user without authentication failures.

### Requirement: Keycloak secret mirrors bootstrap password
`keycloak-secret` SHALL continue to store `KC_BOOTSTRAP_ADMIN_PASSWORD` (set to `POSTGRES_PASSWORD`) so bootstrap can run without requiring an extra password prompt.

#### Scenario: Secret creation stays in sync
- **WHEN** `scripts/run-all.sh` runs fresh
- **THEN** it writes `KC_BOOTSTRAP_ADMIN_PASSWORD` equal to the collected `POSTGRES_PASSWORD` so Keycloak sees the same password in both the database and bootstrap secret.
