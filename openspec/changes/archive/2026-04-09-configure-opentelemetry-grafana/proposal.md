## Why

Currently Grafana only connects to Prometheus for metrics. To enable distributed tracing and broader observability, we need to deploy OpenTelemetry Collector and configure Grafana to consume trace data from it.

## What Changes

- Deploy OpenTelemetry Collector in the infra namespace
- Configure OpenTelemetry to receive OTLP data and export to Prometheus
- Add OpenTelemetry as a datasource in Grafana for tracing visualization

## Capabilities

### New Capabilities
- `opentelemetry-collector`: Deploy and configure OpenTelemetry Collector
- `grafana-otel-datasource`: Configure Grafana to use OpenTelemetry datasource

### Modified Capabilities
- (none)

## Impact

- OpenTelemetry manifests at `infra/services/observability/opentelemetry/`
- Grafana datasource ConfigMap updated

## Non-goals

- Instrumenting individual applications to send traces
- Setting up Jaeger or Tempo as backend (using Prometheus for metrics export)