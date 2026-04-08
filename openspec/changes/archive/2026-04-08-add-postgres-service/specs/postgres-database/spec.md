## ADDED Requirements

### Requirement: PostgreSQL Service Deployment
The system SHALL deploy a PostgreSQL database instance accessible within the Kubernetes cluster.

#### Scenario: PostgreSQL Pod Running
- **WHEN** the PostgreSQL manifest is applied to the cluster
- **THEN** a PostgreSQL pod SHALL be running in the `infra` namespace

### Requirement: Internal Network Access
The system SHALL make PostgreSQL accessible only via internal cluster networking.

#### Scenario: Service Exposed Internally
- **WHEN** a service is created for PostgreSQL
- **THEN** it SHALL be a ClusterIP service not exposed externally

#### Scenario: Internal DNS Resolution
- **WHEN** another pod queries for the PostgreSQL service
- **THEN** it SHALL resolve to `postgres.infra.svc.cluster.local` on port 5432

### Requirement: Persistent Storage
The system SHALL persist database data across pod restarts.

#### Scenario: Data Persists After Restart
- **WHEN** data is written to the database and the pod restarts
- **THEN** the data SHALL remain available after restart

### Requirement: ArgoCD Management
The system SHALL be deployable and manageable through ArgoCD.

#### Scenario: ArgoCD Application Sync
- **WHEN** ArgoCD syncs the postgres application
- **THEN** all PostgreSQL resources SHALL be created in the cluster
