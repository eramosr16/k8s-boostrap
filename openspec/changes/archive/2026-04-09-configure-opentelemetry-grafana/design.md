## Context

Grafana currently only uses Prometheus as a datasource for metrics. OpenTelemetry Collector needs to be deployed to:
1. Collect traces/metrics from applications via OTLP protocol
2. Export metrics to Prometheus for consumption by Grafana
3. Provide a unified observability pipeline

## Goals / Non-Goals

**Goals:**
- Deploy OpenTelemetry Collector with OTLP receiver
- Configure Grafana to query traces from OpenTelemetry
- Maintain Prometheus as default metrics datasource

**Non-Goals:**
- Application instrumentation
- Backend storage for traces (using Prometheus metrics export)

## Decisions

1. **Deployment Mode**: Use Kubernetes Deployment for OpenTelemetry Collector with 1 replica for simplicity

2. **Pipeline Architecture**: 
   - Receivers: OTLP (gRPC and HTTP), jaeger, zipkin
   - Processors: batch
   - Exporters: prometheus, logging

3. **Grafana Integration**: Add Tempo/Prometheus datasource pointing to OpenTelemetry for trace visualization

## Risks / Trade-offs

- [Risk] No applications sending OTLP data → Mitigation: Collector will be ready when apps are instrumented
- [Risk] Resource usage → Mitigation: Start with minimal resources, scale as needed

## Migration Plan

1. Deploy OpenTelemetry Collector manifests
2. Update Grafana datasource ConfigMap
3. Verify connectivity between services

## Open Questions

- Should we use the OpenTelemetry Operator or raw manifests?
- What port should be exposed for OTLP ingestion?