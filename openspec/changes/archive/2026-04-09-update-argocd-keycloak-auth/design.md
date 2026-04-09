## Context

ArgoCD is currently deployed without OIDC authentication, using only local accounts. Keycloak is already deployed and accessible at `auth.mydomain.com`. The goal is to configure ArgoCD to use Keycloak as its OIDC provider and expose it via Traefik at `argocd.mydomain.com`.

## Goals / Non-Goals

**Goals:**
- Configure ArgoCD ConfigMap with Keycloak OIDC settings
- Add Traefik IngressRoute for ArgoCD at argocd.mydomain.com
- Enable secure HTTPS access with existing Let's Encrypt

**Non-Goals:**
- Modifying ArgoCD application sync behavior
- Configuring Keycloak client (assumed pre-configured)
- Setting up SSO for other applications

## Decisions

1. **OIDC Configuration via ConfigMap** - ArgoCD OIDC settings are managed through the `argocd-cm` ConfigMap in the argocd namespace. This is the standard approach and doesn't require custom overlays.

2. **Keycloak Client Settings** - Assumed to be pre-configured in Keycloak with:
   - Client ID: `argocd`
   - Client Protocol: `openid-connect`
   - Valid Redirect URIs: `https://argocd.mydomain.com/*`
   - Web Origins: `https://argocd.mydomain.com`

3. **IngressRoute Structure** - Following the same pattern as existing keycloak-ingressroute.yaml for consistency.

## Risks / Trade-offs

- [Risk] Keycloak client not configured → Mitigation: Document required client setup in tasks
- [Risk] OIDC callback URL mismatch → Mitigation: Ensure redirect URI matches exactly

## Migration Plan

1. Update ArgoCD ConfigMap with OIDC settings
2. Create Traefik IngressRoute for ArgoCD
3. Verify Keycloak client configuration
4. Test login flow

## Open Questions

- What should be the Keycloak client secret reference approach (existing secret or new)?
- Should admin users be mapped from Keycloak groups or local admin preserved?