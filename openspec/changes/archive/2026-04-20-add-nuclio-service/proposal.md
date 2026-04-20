## Why

Nuclio is a high-performance serverless framework that runs on Kubernetes. Adding it to our platform enables users to deploy and manage event-driven functions without managing infrastructure. This completes our platform as a comprehensive development environment.

## What Changes

- Add Nuclio as a new service in `infra/services/nuclio/`
- Deploy Nuclio controller and dashboard to the `nuclio` namespace
- Configure Traefik ingress for the Nuclio dashboard
- Integrate Nuclio dashboard with Keycloak authentication via Traefik OAuth2 plugin
- Add nuclio route to `config.yaml`
- Update `scripts/run-all.sh` to install and configure Nuclio

## Capabilities

### New Capabilities

- `nuclio-service`: Deploy Nuclio controller and dashboard on Kubernetes with Keycloak-authenticated ingress

### Modified Capabilities

- None (new service)

## Non-goals

- Custom function deployments (handled separately)
- Nuclio function scaling configurations

## Impact

- New namespace: `nuclio`
- New routes: `nuclio.${CLUSTER_DOMAIN}`
- New service manifests in `infra/services/`
- Updated `config.yaml` with nuclio route and image versions
- Updated `scripts/run-all.sh` with Nuclio installation