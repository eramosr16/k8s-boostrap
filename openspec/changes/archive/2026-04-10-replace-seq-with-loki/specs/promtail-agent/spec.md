## ADDED Requirements

### Requirement: Promtail runs as a DaemonSet
Promtail SHALL run as a Kubernetes DaemonSet to collect logs from all nodes.

#### Scenario: Promtail DaemonSet deployed in infra namespace
- **WHEN** Promtail manifests are applied to the cluster
- **THEN** a DaemonSet named `promtail` SHALL be created in the `infra` namespace

#### Scenario: Promtail runs on all nodes
- **WHEN** Promtail DaemonSet is deployed
- **THEN** it SHALL have a pod scheduled on every node in the cluster

### Requirement: Promtail collects container logs
Promtail SHALL collect stdout and stderr from all containers in the cluster.

#### Scenario: Promtail reads container logs from /var/log/pods
- **WHEN** Promtail runs as DaemonSet
- **THEN** it SHALL read logs from `/var/log/pods/*/*.log` on each node

#### Scenario: Promtail attaches Kubernetes labels
- **WHEN** Promtail collects a log line
- **THEN** it SHALL attach labels: namespace, pod, container, node

### Requirement: Promtail sends logs to Loki
Promtail SHALL forward collected logs to the Loki service.

#### Scenario: Promtail forwards logs to Loki
- **WHEN** Promtail collects logs
- **THEN** it SHALL send them to `http://loki.infra.svc.cluster.local:3100/loki/api/v1/push`

#### Scenario: Promtail handles Loki unavailability
- **WHEN** Loki is unavailable
- **THEN** Promtail SHALL buffer logs and retry when Loki becomes available

### Requirement: Promtail has appropriate resource limits
Promtail SHALL have resource limits configured to minimize resource consumption.

#### Scenario: Resource limits prevent Promtail from consuming excessive resources
- **WHEN** Promtail DaemonSet is deployed
- **THEN** each pod SHALL have memory limit set to 128Mi

### Requirement: Promtail uses configmap for configuration
Promtail SHALL be configured via a ConfigMap for easy updates without rebuilding the container.

#### Scenario: Promtail configuration is in a ConfigMap
- **WHEN** Promtail is deployed
- **THEN** its configuration SHALL be stored in a ConfigMap named `promtail-config`