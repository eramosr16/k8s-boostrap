## ADDED Requirements

### Requirement: Grafana has Loki datasource configured
Grafana SHALL have a Loki datasource configured for log querying.

#### Scenario: Loki datasource added to Grafana
- **WHEN** Grafana Loki datasource manifest is applied
- **THEN** a datasource named `Loki` SHALL be created in Grafana

#### Scenario: Loki datasource points to internal Loki service
- **WHEN** Loki datasource is configured
- **THEN** URL SHALL be set to `http://loki.infra.svc.cluster.local:3100`

#### Scenario: Loki datasource is accessible in Explore
- **WHEN** user opens Grafana Explore
- **THEN** they SHALL be able to select Loki as the datasource

### Requirement: Loki datasource has access to all namespaces
The Loki datasource SHALL be configured to query logs from all namespaces.

#### Scenario: Loki queries include all namespaces
- **WHEN** user queries logs in Grafana
- **THEN** they SHALL be able to filter by any namespace in the cluster