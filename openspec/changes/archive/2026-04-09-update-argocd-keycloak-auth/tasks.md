## 1. Keycloak Configuration

- [ ] 1.1 Create Keycloak client for ArgoCD (Client authentication disabled, PKCE enabled)
- [ ] 1.2 Configure Valid Redirect URIs: https://argocd.mydomain.com/auth/callback
- [ ] 1.3 Add client scope for groups with Token Mapper (Group Membership)
- [ ] 1.4 Create argocd-admins group and add admin users

## 2. ArgoCD OIDC Configuration

- [x] 2.1 Update argocd-cm ConfigMap with Keycloak OIDC settings (url, issuer, clientID, enablePKCEAuthentication)
- [x] 2.2 Add requestedScopes with openid, profile, email, groups
- [x] 2.3 Configure refreshTokenThreshold (less than Keycloak token lifetime)
- [ ] 2.4 Restart argocd-server pod to apply changes

## 3. ArgoCD RBAC Configuration

- [x] 3.1 Update argocd-rbac-cm ConfigMap with group-to-role mapping
- [x] 3.2 Add policy: g, argocd-admins, role:admin

## 4. Traefik IngressRoute

- [x] 4.1 Create IngressRoute for ArgoCD at argocd.mydomain.com
- [x] 4.2 Configure entryPoint: websecure
- [x] 4.3 Configure TLS with certResolver: le

## 5. Verification

- [ ] 5.1 Test web login flow at https://argocd.mydomain.com
- [ ] 5.2 Test CLI authentication with `argocd login --sso --grpc-web`
- [ ] 5.3 Verify admin access for argocd-admins group members