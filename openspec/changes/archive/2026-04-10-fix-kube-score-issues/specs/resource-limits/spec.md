## ADDED Requirements

### Requirement: All containers have ephemeral storage limits
All containers in Deployments, StatefulSets, and DaemonSets SHALL have ephemeral storage limits configured.

#### Scenario: Deployment has ephemeral storage limits
- **WHEN** a Deployment container is configured
- **THEN** it SHALL include `resources.limits.ephemeral-storage: 500Mi`

#### Scenario: DaemonSet has ephemeral storage limits
- **WHEN** a DaemonSet container is configured
- **THEN** it SHALL include `resources.limits.ephemeral-storage: 500Mi`

#### Scenario: StatefulSet has ephemeral storage limits
- **WHEN** a StatefulSet container is configured
- **THEN** it SHALL include `resources.limits.ephemeral-storage: 500Mi`

### Requirement: Loki StatefulSet has valid serviceName
The Loki StatefulSet SHALL have a valid serviceName configured.

#### Scenario: Loki StatefulSet references existing service
- **WHEN** Loki StatefulSet is deployed
- **THEN** it SHALL have `serviceName: loki` in its spec