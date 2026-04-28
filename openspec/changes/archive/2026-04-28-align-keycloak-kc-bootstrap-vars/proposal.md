## Why

The Camunda Keycloak image we run now only recognizes the `KC_BOOTSTRAP_ADMIN_*` env vars, but our deployment still wires `KEYCLOAK_*` equivalents. As a result, the bootstrap admin user never comes up and Keycloak logs report the missing credentials.

## What Changes

- Switch `infra/services/iam/keycloak/keycloak-deployment.yaml` to export `KC_BOOTSTRAP_ADMIN_USERNAME` and `KC_BOOTSTRAP_ADMIN_PASSWORD`, sourcing both from `keycloak-secret` so the Bitnami/Camunda entrypoint can bootstrap without errors.
- Update automated secret creation (`scripts/run-all.sh`) and documentation so the `keycloak-secret` contains the `KC_BOOTSTRAP_*` keys instead of or alongside the old ones.
- Document the change in `README.md` so operators know which secret keys to keep in sync with Keycloak.

## Capabilities

### New Capabilities
- `keycloak-kc-bootstrap-vars`: Align the Keycloak deployment and onboarding scripts with the `KC_BOOTSTRAP_ADMIN_*` env vars required by the optimized Camunda/Bitnami image.

### Modified Capabilities
- `<existing-name>`: <what requirement is changing>

## Impact

- `infra/services/iam/keycloak/keycloak-deployment.yaml` (deployment manifest environment section)
- `scripts/run-all.sh` (secret generation logic)
- `README.md` (secret table and change log)
- Any automation that rotates Keycloak credentials must now populate the `KC_BOOTSTRAP_ADMIN_*` keys.

## Non-goals

- Changing Keycloak realms, clients, or other authentication flows.
- Migrating away from PostgreSQL or altering database topology.
