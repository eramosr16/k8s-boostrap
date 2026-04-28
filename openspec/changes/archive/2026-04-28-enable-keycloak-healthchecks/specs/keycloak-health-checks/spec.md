## ADDED Requirements

### Requirement: Health endpoints enabled for probes
The Keycloak deployment SHALL set `KC_HEALTH_ENABLED=true`, `KC_HTTP_ENABLED=true`, `KC_PROXY_HEADERS=xforwarded`, and expose `/health/*` endpoints on port 9000 so Kubernetes probes can target them without SSL.

#### Scenario: Health probes reach bitnami endpoints
- **WHEN** the deployment syncs the updated manifest
- **THEN** the container runs with `/health/live`, `/health/ready`, and `/health/started` exposed on port 9000 and does not reject the readiness/liveness HTTP GET requests due to disabled health mode.

### Requirement: Probes target the new port/path
The deployment SHALL add container port 9000 and configure liveness/readiness/startup probes to hit `/health/live`, `/health/ready`, and `/health/started` on that port with sensible delays so the pod doesn’t restart prematurely.

#### Scenario: Probes pass when app starts
- **WHEN** Keycloak starts with the updated probes
- **THEN** Kubernetes sees the pods transition to Ready once `/health/ready` becomes available and keeps them alive while `/health/live` succeeds.
