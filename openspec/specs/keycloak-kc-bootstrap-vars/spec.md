## ADDED Requirements

### Requirement: Deployment exports KC bootstrap variables
The Keycloak deployment SHALL set `KC_BOOTSTRAP_ADMIN_USERNAME` and `KC_BOOTSTRAP_ADMIN_PASSWORD` so the Camunda/Bitnami bootstrap code can create the admin user with no manual intervention.

#### Scenario: Bootstrap credentials are present
- **WHEN** the updated deployment manifest is applied
- **THEN** the resulting Keycloak pod has the two `KC_BOOTSTRAP_ADMIN_*` env vars populated and the logs report `bootstrap-admin-username available only when bootstrap admin password is set` no longer once the container finishes start-up.

### Requirement: Secrets keep providing KC passwords
The `keycloak-secret` shall include the `KC_BOOTSTRAP_ADMIN_PASSWORD` key so rotation scripts and deployments always deliver the password to the pod.

#### Scenario: Secret rotation updates KC key
- **WHEN** automation rotates the Keycloak admin password
- **THEN** it updates `KC_BOOTSTRAP_ADMIN_PASSWORD` in `keycloak-secret` and the deployment picks it up on the next sync without manifest changes.
