## ADDED Requirements

### Requirement: Service account exists in infra realm
Each service SHALL have a service account in the infra realm.

#### Scenario: Grafana service account
- **WHEN** realm clients are created
- **THEN** Grafana client SHALL have serviceAccountsEnabled true

#### Scenario: ArgoCD service account
- **WHEN** realm clients are created
- **THEN** ArgoCD client SHALL have serviceAccountsEnabled true

#### Scenario: Headlamp service account
- **WHEN** realm clients are created
- **THEN** Headlamp client SHALL have serviceAccountsEnabled true

#### Scenario: Seq service account
- **WHEN** realm clients are created
- **THEN** Seq client SHALL have serviceAccountsEnabled true

### Requirement: Service secrets accessible
Service client secrets SHALL be retrievable for Kubernetes secrets.

#### Scenario: Secret retrieval
- **WHEN** client is created
- **THEN** client secret SHALL be retrievable via kcadm

#### Scenario: Secret stored in Kubernetes
- **WHEN** client is created
- **THEN** secret SHALL be stored in Kubernetes secret for the service

### Requirement: Services use infra realm
All services SHALL authenticate against infra realm.

#### Scenario: Service uses correct issuer
- **WHEN** service authenticates
- **THEN** token issuer SHALL be infra realm URL

#### Scenario: Service redirect URIs
- **WHEN** service redirects for auth
- **THEN** redirect URI SHALL match service DNS