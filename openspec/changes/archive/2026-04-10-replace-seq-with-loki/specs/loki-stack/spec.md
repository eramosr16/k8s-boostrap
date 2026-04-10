## ADDED Requirements

### Requirement: Loki runs as a StatefulSet
Loki SHALL run as a Kubernetes StatefulSet with a persistent volume for log storage.

#### Scenario: Loki StatefulSet deployed in infra namespace
- **WHEN** Loki manifests are applied to the cluster
- **THEN** a StatefulSet named `loki` SHALL be created in the `infra` namespace

#### Scenario: Loki has persistent storage
- **WHEN** Loki StatefulSet is deployed
- **THEN** it SHALL have a PersistentVolumeClaim with at least 10Gi storage

#### Scenario: Loki service is internal
- **WHEN** Loki service is created
- **THEN** it SHALL be a ClusterIP service accessible at `loki.infra.svc.cluster.local:3100`

### Requirement: Loki accepts log ingestion via HTTP
Loki SHALL expose an HTTP endpoint for log ingestion compatible with standard clients.

#### Scenario: Promtail can send logs to Loki
- **WHEN** Promtail sends logs to Loki HTTP endpoint
- **THEN** Loki SHALL accept and store the logs

#### Scenario: Applications can send logs via HTTP
- **WHEN** an application sends a POST request to Loki HTTP endpoint
- **THEN** Loki SHALL accept the log entries and store them

### Requirement: Loki integrates with Grafana
Loki SHALL be configured as a datasource in Grafana for unified log viewing.

#### Scenario: Loki datasource exists in Grafana
- **WHEN** Grafana is configured
- **THEN** a Loki datasource SHALL exist pointing to `http://loki.infra.svc.cluster.local:3100`

#### Scenario: Logs are queryable from Grafana Explore
- **WHEN** user navigates to Grafana Explore
- **THEN** they SHALL be able to query Loki and view log entries

### Requirement: Loki has appropriate resource limits
Loki SHALL have resource requests and limits configured to prevent resource exhaustion.

#### Scenario: Resource limits prevent Loki from consuming all node resources
- **WHEN** Loki is deployed
- **THEN** it SHALL have memory limits set (request: 256Mi, limit: 512Mi)

### Requirement: Loki retention policy
Loki SHALL be configured with a retention period for stored logs.

#### Scenario: Logs older than retention period are deleted
- **WHEN** logs exceed the configured retention
- **THEN** Loki SHALL automatically delete old chunks