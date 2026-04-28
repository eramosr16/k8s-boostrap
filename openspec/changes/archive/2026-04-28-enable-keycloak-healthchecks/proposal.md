## Why

Keycloak’s readiness probes currently fail because health endpoints are disabled by default in the Bitnami/Camunda image, so Kubernetes marks the pod as unhealthy and keeps restarting it.

## What Changes

- Enable the `KC_HEALTH_ENABLED` flag (and related runtime flags) so `/health/*` endpoints become available.
- Point the liveness/readiness/startup probes at the new health port/path combination and open the corresponding container port.
- Document the new health check behavior in `README.md` so operators understand the need to pass those env vars when deploying the Keycloak image.

## Capabilities

### New Capabilities
- `keycloak-health-checks`: Health endpoints under `/health` become reachable in the Keycloak deployment, letting Kubernetes readiness/liveness checks succeed.

### Modified Capabilities
- `- None.`

## Impact

- `infra/services/iam/keycloak/keycloak-deployment.yaml` (env vars, ports, probes)
- `README.md` (documenting health check requirements)
- Any onboarding scripts or automation that rely on the deployment manifest running successfully will no longer see the `connect: connection refused` error.

## Non-goals

- Changing the Keycloak authentication realm, clients, or data model.
- Introducing new secrets; environment variables reuse the existing bootstrap credentials and database connection values.
