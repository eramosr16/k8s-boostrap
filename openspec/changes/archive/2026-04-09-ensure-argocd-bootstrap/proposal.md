## Why

Currently, only 5 out of ~10+ services in `infra/services/` have ArgoCD Application definitions (postgres, redis, keycloak, gateway, seq). Services like RabbitMQ, Prometheus, Grafana, OpenTelemetry, and others are not being deployed automatically by ArgoCD. This creates inconsistency and manual deployment burden.

## What Changes

- Create ArgoCD Application manifests for all services that don't have them
- Ensure every service in `infra/services/` has an associated Application for automatic GitOps deployment
- Update existing Application manifests to follow consistent naming convention

## Capabilities

### New Capabilities
- **argocd-auto-bootstrap**: Define the pattern for all services to have ArgoCD Application manifests for automatic deployment

### Modified Capabilities
- None - this is a new capability pattern

## Impact

- All services in `infra/services/` will be automatically deployed by ArgoCD
- Consistent App-of-Apps pattern across all services
- Easier cluster management and reproducibility

## Non-goals

- Modifying the actual service configurations (deployments, services, etc.)
- Changing the root-app.yaml configuration
- Adding new services
