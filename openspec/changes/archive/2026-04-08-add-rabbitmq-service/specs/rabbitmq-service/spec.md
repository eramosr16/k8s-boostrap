## ADDED Requirements

### Requirement: RabbitMQ service shall be deployable in the cluster
The system SHALL provide Kubernetes manifests to deploy RabbitMQ in the infra namespace.

#### Scenario: Deployment applies successfully
- **WHEN** kubectl apply is run on the RabbitMQ manifests
- **THEN** a RabbitMQ pod shall be running in the infra namespace

### Requirement: RabbitMQ shall be accessible internally
The system SHALL expose RabbitMQ via a ClusterIP service on port 5672.

#### Scenario: Service endpoint is resolvable
- **WHEN** other pods query for rabbitmq.infra.svc.cluster.local
- **THEN** the service IP shall be returned

### Requirement: Credentials shall be managed via Kubernetes Secret
The system SHALL store RabbitMQ credentials in a Secret with RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS.

#### Scenario: Secret contains username and password
- **WHEN** kubectl get secret rabbitmq-secret -n infra is executed
- **THEN** the secret shall contain RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS keys

### Requirement: Data shall persist across pod restarts
The system SHALL use a PersistentVolumeClaim to store RabbitMQ data.

#### Scenario: PVC is bound
- **WHEN** RabbitMQ deployment is created
- **THEN** a PVC shall be created and bound to a persistent volume