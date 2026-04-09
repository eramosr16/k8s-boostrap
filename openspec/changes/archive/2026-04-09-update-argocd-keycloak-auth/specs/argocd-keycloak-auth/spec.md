## ADDED Requirements

### Requirement: ArgoCD uses Keycloak OIDC authentication
ArgoCD SHALL authenticate users via Keycloak OIDC provider using PKCE flow for secure authentication.

#### Scenario: User logs in via Keycloak
- **WHEN** user accesses ArgoCD at https://argocd.mydomain.com and clicks login
- **THEN** user is redirected to Keycloak authentication page
- **AND** after successful Keycloak login, user is redirected back to ArgoCD

#### Scenario: CLI authentication with PKCE
- **WHEN** user runs `argocd login argocd.mydomain.com --sso --grpc-web`
- **THEN** CLI opens browser for Keycloak authentication
- **AND** after successful auth, CLI is authenticated

### Requirement: ArgoCD ConfigMap configured for Keycloak OIDC
The argocd-cm ConfigMap in the argo-cd namespace SHALL contain OIDC configuration for Keycloak.

#### Scenario: ConfigMap contains OIDC settings
- **WHEN** argocd-cm ConfigMap is retrieved
- **THEN** it contains url: https://argocd.mydomain.com
- **AND** oidc.config with issuer, clientID, enablePKCEAuthentication, and requestedScopes

### Requirement: Traefik exposes ArgoCD externally
Traefik SHALL route external HTTPS traffic to ArgoCD service at argocd.mydomain.com.

#### Scenario: External access to ArgoCD
- **WHEN** user accesses https://argocd.mydomain.com
- **THEN** request is routed to ArgoCD server service
- **AND** TLS termination occurs at Traefik

### Requirement: Keycloak groups map to ArgoCD roles
Users in Keycloak groups SHALL be mapped to ArgoCD RBAC roles.

#### Scenario: Admin group member accesses ArgoCD
- **WHEN** user belongs to argocd-admins group in Keycloak
- **THEN** user receives role:admin in ArgoCD
- **AND** user can perform admin operations

## MODIFIED Requirements

(None - this is a new capability)

## REMOVED Requirements

(None)