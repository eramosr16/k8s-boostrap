## Why

The cluster needs observability capabilities to monitor application metrics, system performance, and resource usage. Prometheus provides metrics collection and storage while Grafana offers visualization and dashboards. This enables proactive monitoring and troubleshooting.

## What Changes

- Add Prometheus Kubernetes manifests in `infra/services/observability/prometheus/`
- Add Grafana Kubernetes manifests in `infra/services/observability/grafana/`
- Configure Grafana to authenticate via Keycloak OIDC
- Expose Grafana publicly at `metrics.mydomain.com` via Traefik
- Create IngressRoute for secure external access

## Capabilities

### New Capabilities
- `prometheus-service`: Metrics collection and storage with persistent storage
- `grafana-visualization`: Metrics visualization with Keycloak authentication

### Modified Capabilities
- None

## Impact

- New directories: `infra/services/observability/prometheus/`, `infra/services/observability/grafana/`
- Updated: `README.md` (service connection details)

## Non-goals

- Pre-built dashboards (will be created after deployment)
- Alert manager configuration
- High-availability Prometheus (single node for now)