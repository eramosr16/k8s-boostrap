## ADDED Requirements

### Requirement: run-all.sh script orchestrates full bootstrap
The `run-all.sh` script SHALL perform complete cluster setup including K3s, ArgoCD, secrets, and health verification.

#### Scenario: Script installs K3s
- **WHEN** user runs `./scripts/run-all.sh`
- **THEN** script SHALL check if K3s is installed, install if missing, and verify cluster connectivity

#### Scenario: Script installs ArgoCD
- **WHEN** K3s is verified
- **THEN** script SHALL install ArgoCD and wait for it to be ready

#### Scenario: Script prompts for credentials
- **WHEN** ArgoCD is installed
- **THEN** script SHALL prompt user for each service secret (PostgreSQL, Redis, RabbitMQ, Grafana, Keycloak, Seq, Traefik ACME, AWS credentials)

#### Scenario: Script creates Kubernetes secrets
- **WHEN** user provides credentials
- **THEN** script SHALL create secrets in the `infra` namespace using kubectl

#### Scenario: Script configures ArgoCD Application
- **WHEN** secrets are created
- **THEN** script SHALL apply the root-app.yaml to trigger ArgoCD sync

#### Scenario: Script polls for service health
- **WHEN** ArgoCD Application is applied
- **THEN** script SHALL poll cluster until all services reach Healthy status or timeout

#### Scenario: Script exits with appropriate status
- **WHEN** health check completes
- **THEN** script SHALL exit with 0 if all services healthy, non-zero if timeout or error

### Requirement: Interactive credential prompts work securely
Credential prompts SHALL use secure input and validate user input.

#### Scenario: Passwords are not echoed
- **WHEN** user enters password
- **THEN** input SHALL NOT be visible on screen (using `read -s`)

#### Scenario: Empty credentials are rejected
- **WHEN** user enters empty password
- **THEN** script SHALL prompt again until valid input provided

### Requirement: Script handles errors gracefully
The script SHALL handle errors and provide useful feedback.

#### Scenario: K3s installation fails
- **WHEN** K3s installation fails
- **THEN** script SHALL display error message and exit with non-zero status

#### Scenario: ArgoCD installation fails
- **WHEN** ArgoCD installation fails
- **THEN** script SHALL display error message and exit with non-zero status

#### Scenario: Service health check times out
- **WHEN** services don't become healthy within timeout
- **THEN** script SHALL display which services are unhealthy and exit with non-zero status
