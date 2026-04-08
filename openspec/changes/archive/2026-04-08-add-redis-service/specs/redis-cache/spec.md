## ADDED Requirements

### Requirement: Redis Service Deployment
The system SHALL deploy a Redis cache instance accessible within the Kubernetes cluster.

#### Scenario: Redis Pod Running
- **WHEN** the Redis manifest is applied to the cluster
- **THEN** a Redis pod SHALL be running in the `infra` namespace

### Requirement: Internal Network Access
The system SHALL make Redis accessible only via internal cluster networking.

#### Scenario: Service Exposed Internally
- **WHEN** a service is created for Redis
- **THEN** it SHALL be a ClusterIP service not exposed externally

#### Scenario: Internal DNS Resolution
- **WHEN** another pod queries for the Redis service
- **THEN** it SHALL resolve to `redis.infra.svc.cluster.local` on port 6379

### Requirement: Persistent Storage
The system SHALL persist cache data across pod restarts when persistence is enabled.

#### Scenario: Data Persists After Restart
- **WHEN** data is written to Redis and the pod restarts
- **THEN** the data SHALL remain available after restart

### Requirement: ArgoCD Management
The system SHALL be deployable and manageable through ArgoCD.

#### Scenario: ArgoCD Application Sync
- **WHEN** ArgoCD syncs the redis application
- **THEN** all Redis resources SHALL be created in the cluster
