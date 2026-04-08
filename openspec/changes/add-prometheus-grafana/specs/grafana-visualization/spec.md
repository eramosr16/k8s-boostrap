## ADDED Requirements

### Requirement: Grafana service shall be deployable in the cluster
The system SHALL provide Kubernetes manifests to deploy Grafana in the infra namespace.

#### Scenario: Deployment applies successfully
- **WHEN** kubectl apply is run on the Grafana manifests
- **THEN** a Grafana pod shall be running in the infra namespace

### Requirement: Grafana shall be accessible internally
The system SHALL expose Grafana via a ClusterIP service on port 3000.

#### Scenario: Service endpoint is resolvable
- **WHEN** other pods query for grafana.infra.svc.cluster.local
- **THEN** the service IP shall be returned

### Requirement: Grafana shall authenticate via Keycloak OIDC
The system SHALL configure Grafana to use Keycloak as the OIDC provider for authentication.

#### Scenario: User accesses Grafana
- **WHEN** a user navigates to Grafana
- **THEN** they shall be redirected to Keycloak for authentication

### Requirement: Grafana shall be accessible externally at metrics.mydomain.com
The system SHALL expose Grafana via a Traefik IngressRoute.

#### Scenario: External access
- **WHEN** user navigates to https://metrics.mydomain.com
- **THEN** Grafana shall be served over HTTPS with valid certificate

### Requirement: Dashboard data shall persist across restarts
The system SHALL use a PersistentVolumeClaim to store Grafana dashboards.

#### Scenario: PVC is bound
- **WHEN** Grafana deployment is created
- **THEN** a PVC shall be created and bound to a persistent volume