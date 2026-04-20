## 1. Configuration Updates

- [x] 1.1 Add nuclio route to config.yaml (routes.nuclio: nuclio)
- [x] 1.2 Add nuclio image version to config.yaml (images.nuclio: latest)
- [x] 1.3 Add nuclio helm chart repo to config (nuclio.io/charts)
- [x] 1.4 Add ECR registry URL to config.yaml for function images
- [x] 1.5 Add RabbitMQ service URL to config for Nuclio broker

## 2. Helm Deployment Setup

- [x] 2.1 Add Nuclio Helm chart repository
- [x] 2.2 Create Helm values file for production deployment
- [x] 2.3 Configure registry credentials (reuse infra/services/registry/)
- [x] 2.4 Configure Kaniko as container builder

## 3. Nuclio Service Setup (Helm)

- [x] 3.1 Create namespace nuclio
- [x] 3.2 Create docker-registry secret for ECR (use existing registry)
- [x] 3.3 Create AWS credentials secret (use existing registry)
- [x] 3.4 Install Nuclio via Helm chart
- [ ] 3.5 Verify controller and dashboard pods running

## 4. ECR Integration

- [x] 4.1 Create ECR token secret (use existing registry service)
- [x] 4.2 Configure registry.pushPullUrl for function images
- [ ] 4.3 Configure kaniko.cacheRepo for ECR compatibility
- [x] 4.4 Set up ECR token refresh cron job (use existing)

## 5. Platform Configuration (ConfigMap)

- [x] 5.1 Create platform-config ConfigMap in nuclio namespace
- [x] 5.2 Configure Prometheus pullmetrics sink for system metrics
- [x] 5.3 Configure Prometheus pushmetrics for function metrics
- [x] 5.4 Configure stdout logger sink for function logs
- [x] 5.5 Configure RabbitMQ as default broker (use existing broker service)
- [x] 5.6 Configure runtime envFrom for RabbitMQ credentials (use existing secret)

## 6. Prometheus Metrics Integration

- [x] 6.1 Create ServiceMonitor for Nuclio metrics scraping
- [x] 6.2 Configure metrics.prometheusPull URL in platform-config
- [ ] 6.3 Verify metrics appear in Prometheus
- [ ] 6.4 Create Grafana dashboard for Nuclio functions

## 7. RabbitMQ Broker Integration

- [x] 7.1 Configure default broker URL in platform-config
- [x] 7.2 Create RabbitMQ secret for function access (reuse existing broker)
- [ ] 7.3 Test rabbitmq trigger in function
- [x] 7.4 Document broker configuration for functions

## 8. Multi-Tenancy Support

- [x] 8.1 Configure controller.namespace for single-tenant scope
- [x] 8.2 Document multi-namespace deployment pattern
- [x] 8.3 Create RBAC configuration for tenant isolation

## 9. ArgoCD Application

- [x] 9.1 Create Helm-based ArgoCD application for Nuclio
- [x] 9.2 Add nuclio to root-app.yaml if needed

## 10. Traefik Ingress with OAuth2

- [x] 10.1 Create infra/services/nuclio/ middleware.yaml (OAuth2 forwardauth)
- [x] 10.2 Create infra/services/nuclio/ ingressroute.yaml (HTTPS ingress)

## 11. Bootstrap Script Updates

- [x] 11.1 Add nuclio route to load_cluster_config
- [x] 11.2 Add ECR configuration loading
- [x] 11.3 Add RabbitMQ configuration loading
- [x] 11.4 Add install_nuclio function (Helm-based)
- [x] 11.5 Add nuclio to main() function call order

## 12. Version Management

- [x] 12.1 Document version freeze process (in README.md)
- [ ] 12.2 Add upgrade testing checklist

## 13. Verification

- [ ] 13.1 Verify Nuclio pods: kubectl -n nuclio get pods
- [ ] 13.2 Test dashboard at https://nuclio.cluster.local
- [ ] 13.3 Verify OAuth2 redirect to Keycloak
- [ ] 13.4 Test function deployment via nuctl
- [ ] 13.5 Verify ECR image push/pull works
- [ ] 13.6 Verify Prometheus metrics scraping
- [ ] 13.7 Verify RabbitMQ trigger works