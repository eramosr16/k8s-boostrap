## Context

The k8s-bootstrap project uses ArgoCD to manage Kubernetes manifests. It already includes Keycloak for identity management. Prometheus and Grafana need to be added for observability with Grafana authenticating via Keycloak and exposed at metrics.mydomain.com.

## Goals / Non-Goals

**Goals:**
- Deploy Prometheus in `infra` namespace with persistent storage
- Deploy Grafana in `infra` namespace with Keycloak OIDC authentication
- Expose Grafana via Traefik IngressRoute at `metrics.mydomain.com`
- Configure Grafana to use Keycloak client for OIDC

**Non-Goals:**
- Pre-configured dashboards
- AlertManager
- High-availability setup

## Decisions

1. **Prometheus**: Use `prom/prometheus` image with PVC for storage
2. **Grafana**: Use `grafana/grafana` image with persistence for dashboards
3. **Authentication**: Keycloak OIDC with client configuration
4. **Ingress**: Traefik IngressRoute with middleware for security headers
5. **Storage**: 50Gi PVC for Prometheus, 10Gi for Grafana

## Risks / Trade-offs

- [Risk] Keycloak not reachable → [Mitigation] Grafana falls back to basic auth (disabled)
- [Risk] Large metrics storage → [Mitigation] Set retention and storage limits
- [Risk] Public exposure → [Mitigation] Use HTTPS only, security headers middleware

## Migration Plan

1. Create Keycloak client for Grafana
2. Deploy Prometheus (deployment + service + PVC)
3. Deploy Grafana (deployment + service + PVC + config for OIDC)
4. Create IngressRoute for metrics.mydomain.com
5. Verify access