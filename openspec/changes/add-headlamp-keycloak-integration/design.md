## Context

Headlamp is currently deployed with service account token authentication. Users must run `kubectl create token headlamp -n infra` to get a login token. Integrating with Keycloak OIDC will allow users to authenticate using their Keycloak credentials, providing a better user experience aligned with existing Grafana and ArgoCD integration.

## Goals / Non-Goals

**Goals:**
- Configure Headlamp to authenticate via Keycloak OIDC
- Automatically create Keycloak client during bootstrap
- Store OIDC client credentials in Kubernetes secret
- Use OIDC impersonation mode (Headlamp handles auth, passes user info via impersonation headers)

**Non-Goals:**
- Configuring Kubernetes API server OIDC flags (not needed with Headlamp's impersonation)
- Custom CA certificates for OIDC
- Group-based RBAC mapping in Keycloak

## Decisions

1. **OIDC Configuration via Environment Variables**: Use environment variables in the deployment rather than Helm values, since we're using plain YAML manifests
   - Alternative: Use config file - Rejected: Environment variables are simpler for our manifest-based setup

2. **OIDC Impersonation Mode**: Configure Headlamp to use the service account with impersonation
   - This allows Headlamp to validate OIDC tokens and impersonate the user when calling the Kubernetes API
   - Requires ClusterRole with impersonation permissions

3. **Keycloak Client Settings**:
   - Client ID: `headlamp`
   - Access Type: Confidential
   - Standard Flow Enabled: true
   - Valid Redirect URIs: `https://headlamp.mydomain.com/*`, `http://localhost:4466/*`
   - Scopes: `openid`, `email`, `profile`

4. **Secret Storage**: Store OIDC credentials in `headlamp-oidc-secret` in the `infra` namespace
   - Contains: OIDC_CLIENT_ID, OIDC_CLIENT_SECRET, OIDC_ISSUER_URL

## Risks / Trade-offs

- **Risk**: OIDC callback URL mismatch
  - **Mitigation**: Configure correct redirect URIs in Keycloak client

- **Risk**: Keycloak not ready when Headlamp starts
  - **Mitigation**: Add startup probe/liveness check; Keycloak should be ready before Headlamp in deployment order

- **Risk**: Users seeing "anonymous" after OIDC login
  - **Mitigation**: Ensure OIDC_USE_ACCESS_TOKEN is set correctly and ClusterRole allows impersonation

## Migration Plan

1. Update `headlamp-deployment.yaml` to add OIDC environment variables
2. Create `headlamp-oidc-secret.yaml` with OIDC credentials
3. Update `headlamp-clusterrole.yaml` to add impersonation permissions
4. Update `scripts/run-all.sh` to:
   - Create Keycloak client "headlamp"
   - Retrieve client secret
   - Create/update the OIDC secret

## Open Questions

- Should we keep service account token as fallback authentication method?
  - Decision: Yes, keep it as backup for cluster admin access