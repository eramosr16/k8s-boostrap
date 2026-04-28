## Why

The Bitnami Keycloak image we switched to now only enables the bootstrap admin user when `KEYCLOAK_BOOTSTRAP_ADMIN_USERNAME` and `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` are present. The current manifest still wires the older `KEYCLOAK_ADMIN_*` env vars, so the new image never creates the admin user and the bootstrap step fails.

## What Changes

- Update `infra/services/iam/keycloak/keycloak-deployment.yaml` to set the bootstrap-specific environment variables that the Bitnami runtime expects, sourcing secrets for both passwords so no credentials leak.
- Document the behavior in `README.md` so future maintainers know which env vars and secret keys must be kept in sync with Keycloak’s bootstrap requirements.

## Capabilities

### New Capabilities
- `keycloak-bootstrap-env`: Ensure the Keycloak deployment provides the `KEYCLOAK_BOOTSTRAP_ADMIN_*` variables and the matching database credentials so Bitnami’s bootstrap sequence can succeed.

### Modified Capabilities
- `<existing-name>`: <what requirement is changing>

## Impact

- `infra/services/iam/keycloak/keycloak-deployment.yaml` (deployment manifest including secrets)
- `README.md` (change log entry describing the env vars)
- Any automation that regenerates `keycloak-secret` must continue to supply the new key names so the deployment can read them at runtime.

## Non-goals

- Introducing new Keycloak realms, clients, or authentication flows.
- Changing the database host/service name beyond the existing `postgres` service.
