## ADDED Requirements

### Requirement: Prometheus service shall be deployable in the cluster
The system SHALL provide Kubernetes manifests to deploy Prometheus in the infra namespace.

#### Scenario: Deployment applies successfully
- **WHEN** kubectl apply is run on the Prometheus manifests
- **THEN** a Prometheus pod shall be running in the infra namespace

### Requirement: Prometheus shall be accessible internally
The system SHALL expose Prometheus via a ClusterIP service on port 9090.

#### Scenario: Service endpoint is resolvable
- **WHEN** other pods query for prometheus.infra.svc.cluster.local
- **THEN** the service IP shall be returned

### Requirement: Metrics shall persist across pod restarts
The system SHALL use a PersistentVolumeClaim to store Prometheus data.

#### Scenario: PVC is bound
- **WHEN** Prometheus deployment is created
- **THEN** a PVC shall be created and bound to a persistent volume

### Requirement: Prometheus shall scrape metrics from cluster services
The system SHALL include a ServiceMonitor or PodMonitor configuration for key services.

#### Scenario: ServiceMonitor is configured
- **WHEN** Prometheus is deployed
- **THEN** it shall have configuration to scrape metrics from services in the cluster