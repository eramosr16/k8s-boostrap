## ADDED Requirements

### Requirement: Keycloak infra realm exists
The Keycloak SHALL have an `infra` realm created during bootstrap.

#### Scenario: Realm creation requested
- **WHEN** run-all.sh creates the infra realm
- **THEN** realm SHALL be created with OIDC enabled

#### Scenario: Realm has OIDC configuration
- **WHEN** infra realm is created
- **THEN** realm SHALL support OpenID Connect protocol

#### Scenario: Realm has proper settings
- **WHEN** infra realm is created
- **THEN** realm SHALL have loginWithEmail allowed, duplicateEmails allowed

### Requirement: infra realm clients exist
The infra realm SHALL have OAuth clients for cluster services.

#### Scenario: k3s-api client exists
- **WHEN** realm is created
- **THEN** client `k3s-api` SHALL exist with OIDC protocol

#### Scenario: Service clients exist
- **WHEN** realm is created
- **THEN** clients for Grafana, ArgoCD, Headlamp, Seq SHALL exist

#### Scenario: Clients have correct redirect URIs
- **WHEN** clients are created
- **THEN** redirect URIs SHALL include service internal DNS names

### Requirement: Service accounts enabled
Service accounts SHALL be enabled for each client.

#### Scenario: Service account feature
- **WHEN** clients are created
- **THEN** serviceAccountsEnabled SHALL be true

#### Scenario: Client credentials retrieved
- **WHEN** clients are created
- **THEN** client secrets SHALL be retrievable via kcadm