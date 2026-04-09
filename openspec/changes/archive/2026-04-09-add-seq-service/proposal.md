## Why

We need a centralized log aggregation and analysis platform. Seq provides structured log aggregation with a web UI, and it can consume data directly from OpenTelemetry Collector for log processing and visualization.

## What Changes

- Deploy Seq in the infra namespace
- Configure Seq to receive logs via HTTP from OpenTelemetry Collector
- Expose Seq publicly at logs.mydomain.com via Traefik IngressRoute
- Use environment variables for admin credentials

## Capabilities

### New Capabilities
- `seq-service`: Deploy and configure Seq log aggregation service

### Modified Capabilities
- (none)

## Impact

- Seq manifests at `infra/services/observability/seq/`
- Traefik configuration - new IngressRoute for Seq
- OpenTelemetry configuration - add Seq as log exporter

## Non-goals

- Setting up Seq authentication beyond admin credentials
- Configuring log retention policies