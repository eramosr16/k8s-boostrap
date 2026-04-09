## Requirements

### Requirement: All services have ArgoCD Application manifests
Each service directory under `infra/services/` SHALL have an ArgoCD Application manifest file named `<service>-app.yaml` that enables automatic GitOps deployment.

#### Scenario: Service with Application manifest deploys automatically
- **WHEN** a service directory contains a `<service>-app.yaml` file
- **THEN** ArgoCD SHALL detect and deploy the service automatically

#### Scenario: Application uses consistent naming
- **WHEN** creating a new Application manifest
- **THEN** the Application name SHALL match the directory name (e.g., `rabbitmq` for `broker/rabbitmq/`)

#### Scenario: Application targets correct namespace
- **WHEN** Application manifest is created
- **THEN** it SHALL target the `infra` namespace

#### Scenario: Application uses automated sync policy
- **WHEN** Application manifest is created
- **THEN** it SHALL include `automated.prune: true` and `automated.selfHeal: true`

### Requirement: Missing services receive Application manifests
Services currently lacking Application manifests SHALL have new ones created.

#### Scenario: RabbitMQ gets Application manifest
- **WHEN** RabbitMQ service is missing an Application manifest
- **THEN** a `rabbitmq-app.yaml` SHALL be created in `infra/services/broker/rabbitmq/`

#### Scenario: Prometheus gets Application manifest
- **WHEN** Prometheus service is missing an Application manifest
- **THEN** a `prometheus-app.yaml` SHALL be created in `infra/services/observability/prometheus/`

#### Scenario: Grafana gets Application manifest
- **WHEN** Grafana service is missing an Application manifest
- **THEN** a `grafana-app.yaml` SHALL be created in `infra/services/observability/grafana/`

#### Scenario: OpenTelemetry gets Application manifest
- **WHEN** OpenTelemetry service is missing an Application manifest
- **THEN** a `opentelemetry-app.yaml` SHALL be created in `infra/services/observability/opentelemetry/`

#### Scenario: ArgoCD gets Application manifest
- **WHEN** ArgoCD service is missing an Application manifest
- **THEN** an `argocd-app.yaml` SHALL be created in `infra/services/observability/argocd/`

### Requirement: Existing Applications follow consistent pattern
All existing Application manifests SHALL follow the same structure and sync policy.

#### Scenario: Existing Applications have automated sync
- **WHEN** reviewing existing Application manifests
- **THEN** they SHALL all have `syncPolicy.automated` configured with `prune` and `selfHeal`
