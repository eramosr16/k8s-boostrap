## 1. Create Prometheus manifests

- [x] 1.1 Create infra/services/observability/prometheus/ directory
- [x] 1.2 Create prometheus-deployment.yaml with prom/prometheus image
- [x] 1.3 Create prometheus-service.yaml (ClusterIP on port 9090)
- [x] 1.4 Create prometheus-pvc.yaml for metrics storage (50Gi)
- [x] 1.5 Create prometheus-config.yaml with basic scrape configs

## 2. Create Grafana manifests

- [x] 2.1 Create infra/services/observability/grafana/ directory
- [x] 2.2 Create grafana-deployment.yaml with grafana/grafana image
- [x] 2.3 Create grafana-service.yaml (ClusterIP on port 3000)
- [x] 2.4 Create grafana-pvc.yaml for dashboard storage (10Gi)
- [x] 2.5 Create grafana-config.yaml with Keycloak OIDC configuration
- [x] 2.6 Create grafana-datasource-config.yaml pointing to Prometheus

## 3. Configure external access

- [x] 3.1 Create Traefik IngressRoute for metrics.mydomain.com
- [x] 3.2 Add TLS configuration for HTTPS
- [x] 3.3 Add security headers middleware

## 4. Update documentation

- [x] 4.1 Add Prometheus and Grafana to README.md service connection table
- [x] 4.2 Add Grafana OIDC configuration to secrets table