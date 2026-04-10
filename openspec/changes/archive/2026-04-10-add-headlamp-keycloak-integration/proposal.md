## Why

Headlamp currently uses service account token authentication. Integrating with Keycloak OIDC will provide secure user authentication using existing Keycloak users, following the same pattern used for Grafana and ArgoCD. This enables SSO without managing separate credentials.

## What Changes

- Add OIDC configuration to Headlamp deployment via environment variables
- Create Keycloak client "headlamp" in master realm (similar to grafana/argocd)
- Store OIDC credentials in a Kubernetes secret
- Update scripts/run-all.sh to automatically create Keycloak client and retrieve client secret

## Capabilities

### New Capabilities
- `headlamp-keycloak-auth`: OIDC authentication via Keycloak for Headlamp dashboard

### Modified Capabilities
- `headlamp-dashboard`: Update existing spec to include OIDC authentication option

## Non-goals

- Configuring Kubernetes API server OIDC flags (Headlamp can handle OIDC without this using impersonation)
- Custom CA certificates for OIDC (use default system trust)
- Group-based RBAC mapping (future enhancement)

## Impact

- `infra/services/observability/headlamp/headlamp-deployment.yaml`: Add OIDC environment variables
- `infra/services/observability/headlamp/headlamp-secret.yaml`: Add OIDC credentials secret
- `scripts/run-all.sh`: Add Headlamp Keycloak client creation