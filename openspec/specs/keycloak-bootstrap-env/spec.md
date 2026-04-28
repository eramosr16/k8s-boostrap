## ADDED Requirements

### Requirement: Keycloak bootstrap env vars align with Bitnami expectations
The Keycloak deployment SHALL expose `KEYCLOAK_BOOTSTRAP_ADMIN_USERNAME` and `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` environment variables populated from `keycloak-secret`, ensuring the Bitnami image can complete its bootstrap process.

#### Scenario: Bitnami image sees bootstrap credentials
- **WHEN** ArgoCD applies the deployment manifest
- **THEN** the resulting Keycloak pod is created with `KEYCLOAK_BOOTSTRAP_ADMIN_USERNAME` and `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` from the secret and the logs show the bootstrap admin user being configured without errors.

### Requirement: Existing automation updates secret keys
Any automation that rotates Keycloak credentials SHALL update `keycloak-secret` to include `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` so the deployment always has the password.

#### Scenario: Secret rotation maintains compatibility
- **WHEN** an operator updates the admin password via automation
- **THEN** the automation writes the new value under `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` and the deployment picks it up on the next sync without needing manifest changes.
