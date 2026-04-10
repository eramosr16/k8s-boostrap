## ADDED Requirements

### Requirement: K3s API server uses Keycloak OIDC
The K3s API server SHALL be configured to authenticate against Keycloak infra realm.

#### Scenario: OIDC configuration present
- **WHEN** K3s is configured
- **THEN** kube-apiserver-arg flags SHALL include OIDC settings

#### Scenario: OIDC issuer URL
- **WHEN** K3s is configured
- **THEN** oidc-issuer-url SHALL point to Keycloak infra realm

#### Scenario: OIDC username claim
- **WHEN** K3s is configured
- **THEN** oidc-username-claim SHALL be set (preferred_username or sub)

#### Scenario: OIDC client ID
- **WHEN** K3s is configured
- **THEN** oidc-client-id SHALL match k3s-api client in infra realm

### Requirement: K3s OIDC works with Keycloak
Users SHALL be able to authenticate to K3s via Keycloak.

#### Scenario: User authenticates
- **WHEN** user logs in via Keycloak
- **THEN** user identity is mapped to Kubernetes RBAC

#### Scenario: RBAC binding exists
- **WHEN** OIDC is configured
- **THEN** cluster-admin ClusterRoleBinding exists for admin users

### Requirement: kubectl works with OIDC
The kubectl SHALL work with Keycloak tokens.

#### Scenario: Token request
- **WHEN** user requests token from Keycloak
- **THEN** token is valid for Kubernetes API

#### Scenario: Token refresh
- **WHEN** token expires
- **THEN** user can request new token without re-authenticating