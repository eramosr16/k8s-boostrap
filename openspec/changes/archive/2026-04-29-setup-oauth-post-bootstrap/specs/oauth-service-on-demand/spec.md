## ADDED Requirements

### Requirement: Post-bootstrap OAuth recovery script exists
The system SHALL provide a script (`scripts/setup-oauth-after-bootstrap.sh`) that operators can run once Kubernetes, PostgreSQL, and Keycloak are healthy to finish configuring the Keycloak realm and clients without rerunning the full bootstrap.

#### Scenario: Operator recovers OAuth after failed bootstrap
- **WHEN** the cluster is up, PostgreSQL and Keycloak pods report READY, and the bootstrap run previously exited due to Keycloak unavailability
- **THEN** the operator executes the script with the same credential environment variables used during bootstrap, and the script completes with exit code 0

### Requirement: Keycloak infra realm and clients are ensured
The script SHALL wait for the Keycloak health endpoint, create or verify the `infra` realm, and create Grafana, ArgoCD, and Headlamp clients with the same redirect URIs as the bootstrap script, retrying once if the realm already exists.

#### Scenario: Keycloak clients already exist
- **WHEN** the script runs and Keycloak already contains the `infra` realm and the required clients
- **THEN** the script logs that each resource exists, does not fail, and proceeds to fetch the current client secrets

### Requirement: Service secrets are synchronized with Keycloak client secrets
After ensuring the clients exist, the script SHALL fetch the OIDC client secrets via `kcadm get clients/.../client-secret` and update the corresponding Kubernetes secrets (`grafana-secret`, `argocd-secret`, `headlamp-oidc-secret`) so downstream services can authenticate.

#### Scenario: Secrets refresh
- **WHEN** the script updates a service secret
- **THEN** the secret contains the latest client secret, and the script outputs which service secrets were refreshed

### Requirement: Script documents recovery steps
The repository SHALL document how to run the OAuth recovery script, including required environment variables and verification steps, so new operators can discover the recovery path.

#### Scenario: Operator follows docs
- **WHEN** an operator reads the README section added for this change
- **THEN** they can run the script with the proper credentials and verify Grafana/ArgoCD/Headlamp access via Keycloak
