## ADDED Requirements

### Requirement: Grafana has OpenTelemetry datasource
Grafana SHALL have a configured datasource pointing to OpenTelemetry Collector for trace visualization.

#### Scenario: Grafana queries traces from OTel
- **WHEN** user navigates to Explore in Grafana
- **THEN** they can select the OpenTelemetry datasource to query traces

### Requirement: Grafana Prometheus datasource remains primary
Grafana SHALL keep Prometheus as the default datasource for metrics.

#### Scenario: Default datasource is Prometheus
- **WHEN** user creates a new dashboard
- **THEN** Prometheus is selected as default datasource

## MODIFIED Requirements

(None)

## REMOVED Requirements

(None)