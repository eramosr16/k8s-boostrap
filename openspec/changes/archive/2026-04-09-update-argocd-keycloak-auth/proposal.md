## Why

ArgoCD currently has no external authentication mechanism configured, relying on local accounts. Integrating Keycloak as an OIDC provider will provide centralized authentication, role-based access control, and improved security for the ArgoCD UI.

## What Changes

- Configure ArgoCD to use Keycloak as OIDC provider for authentication
- Add Traefik IngressRoute for external access to ArgoCD at argocd.mydomain.com
- Configure TLS for the ArgoCD ingress using existing Traefik TLS configuration

## Capabilities

### New Capabilities
- `argocd-keycloak-auth`: Configure ArgoCD OIDC authentication with Keycloak

### Modified Capabilities
- (none)

## Impact

- ArgoCD at `infra/services/observability/argocd/` - modify ConfigMap for OIDC config
- Traefik configuration at `infra/services/gateway/` - new IngressRoute for ArgoCD

## Non-goals

- Modifying ArgoCD application sync behavior
- Configuring Keycloak client settings (already assumed to exist)
- Setting up SSO for other applications