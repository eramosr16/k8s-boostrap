## Context

- The Camunda/Bitnami Keycloak container relies on the same PostgreSQL server that our `postgres` StatefulSet provisions, but the Keycloak manifest pulls its database password from `keycloak-secret`, a separate secret populated from a user prompt.
- Logs show Keycloak failing with `password authentication failed for user "postgres"` because the value in `keycloak-secret` can drift from the `POSTGRES_PASSWORD` that the database actually uses.
- Keeping two independent credential prompts is error prone; we can eliminate the drift by reusing `POSTGRES_PASSWORD` directly.

## Goals / Non-Goals

**Goals:**

- Configure the Keycloak deployment to read `KEYCLOAK_DATABASE_PASSWORD` from `postgres-secret` so it always matches the database’s password.
- Update the onboarding script to stop prompting for a separate Keycloak database password and instead copy `POSTGRES_PASSWORD` into the Keycloak secret where needed.
- Document this coupling in `README.md` so operators know Keycloak piggybacks on the Postgres credentials.

**Non-Goals:**

- Creating a second PostgreSQL user or database specifically for Keycloak.
- Introducing new secrets or automation outside the existing `postgres-secret` and `keycloak-secret` pairings.

## Decisions

- Reference `postgres-secret` in the Keycloak deployment for the database password rather than duplicating the value inside the Keycloak secret. This keeps the authoritative credential in one place.
- Keep the Keycloak secret for bootstrap credentials (`KC_BOOTSTRAP_*`) and admin password only, and set `KEYCLOAK_DATABASE_PASSWORD` during secret creation using `$POSTGRES_PASSWORD` so automation stays consistent.
- Remove the standalone prompt for the Keycloak database password but keep the prompt for `POSTGRES_PASSWORD` so the bootstrap process still collects the necessary credential.

## Risks / Trade-offs

- [Secret propagation] If automation writes `POSTGRES_PASSWORD` but not the Keycloak secret, Keycloak won’t know the password; mitigation is to copy the value explicitly when creating `keycloak-secret` (as part of this change).
- [Manual overrides] Operators who previously set a different Keycloak database password will lose that ability; mitigation is to document the change and note that Postgres and Keycloak now share the same password.

## Migration Plan

1. Update `scripts/run-all.sh` so the Keycloak secret includes `KC_BOOTSTRAP_ADMIN_*` values and copies `KEYCLOAK_DATABASE_PASSWORD` from `$POSTGRES_PASSWORD`, removing the separate prompt.
2. Modify `infra/services/iam/keycloak/keycloak-deployment.yaml` to load `KEYCLOAK_DATABASE_PASSWORD` from `postgres-secret` instead of the Keycloak secret.
3. Adjust README entries to describe that Keycloak reuses Postgres’ credentials and record the new change in the recent updates section.
4. Validate the deployment with `kubectl apply --dry-run=client` and ensure the Keycloak pod can start after the new config is pushed.

## Open Questions

- Should we remove the `KEYCLOAK_DATABASE_PASSWORD` entry from `CREDENTIAL_PROMPTS` entirely, or keep it for backwards compatibility while ignoring the value?
