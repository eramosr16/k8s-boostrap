## ADDED Requirements

### Requirement: Nuclio Controller Running
The Nuclio controller SHALL be deployed and running in the `nuclio` namespace on Kubernetes.

#### Scenario: Controller pod running
- **WHEN** Nuclio manifests are applied to the cluster
- **THEN** a controller pod with label `app.kubernetes.io/name=nuclio` exists in namespace `nuclio`
- **AND** the pod status shows `Running` with `Ready: True`

#### Scenario: Controller responds to CRDs
- **WHEN** a Function CRD is created in the nuclio namespace
- **THEN** the controller detects and processes the CR

### Requirement: Nuclio Dashboard Accessible
The Nuclio dashboard SHALL be accessible via HTTPS through Traefik ingress.

#### Scenario: Dashboard service exists
- **WHEN** Nuclio dashboard deployment is applied
- **THEN** a service `nuclio-ingress` exists in namespace `nuclio` exposing port 8080

#### Scenario: Dashboard reachable via ingress
- **WHEN** user navigates to `https://nuclio.${CLUSTER_DOMAIN}`
- **THEN** the request is routed to the Nuclio dashboard pod

### Requirement: Dashboard Authenticated via Keycloak
The Nuclio dashboard SHALL require authentication through Keycloak OAuth2.

#### Scenario: Unauthenticated access redirected
- **WHEN** unauthenticated user visits the dashboard URL
- **THEN** the user is redirected to Keycloak login

#### Scenario: Authenticated access granted
- **WHEN** user authenticates via Keycloak
- **THEN** the user is redirected back to the Nuclio dashboard

### Requirement: Function Deployment Works
Users SHALL be able to deploy functions to Nuclio.

#### Scenario: Function CR created
- **WHEN** a Function custom resource is applied to the cluster
- **THEN** the controller creates a deployment for the function
- **AND** the function becomes invocable via its HTTP trigger

## ADDED Requirements

### Requirement: Nuclio Installed via ArgoCD
The Nuclio service SHALL be deployable through ArgoCD as part of the platform.

#### Scenario: Nuclio Application synced
- **WHEN** ArgoCD syncs the nuclio application
- **THEN** all Nuclio resources are applied to the cluster
- **AND** the nuclio namespace contains controller and dashboard pods

### Requirement: Prometheus Metrics Available
The Nuclio service SHALL expose Prometheus metrics for monitoring.

#### Scenario: System metrics via pull
- **WHEN** Prometheus scrapes the Nuclio metrics endpoint
- **THEN** Nuclio system metrics appear in Prometheus

#### Scenario: Function metrics exported
- **WHEN** a function is deployed
- **THEN** function execution metrics are exported to Prometheus

### Requirement: RabbitMQ as Default Broker
The Nuclio platform SHALL use RabbitMQ as the default message broker.

#### Scenario: Broker configured
- **WHEN** platform-config ConfigMap is created
- **THEN** default broker URL points to RabbitMQ in infra namespace

#### Scenario: RabbitMQ trigger works
- **WHEN** a function with rabbitmq trigger is deployed
- **THEN** the function receives messages from RabbitMQ