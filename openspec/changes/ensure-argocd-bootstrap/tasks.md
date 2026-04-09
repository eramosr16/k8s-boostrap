## 1. Create ArgoCD Application Manifests

- [x] 1.1 Create `rabbitmq-app.yaml` in `infra/services/broker/rabbitmq/`
- [x] 1.2 Create `prometheus-app.yaml` in `infra/services/observability/prometheus/`
- [x] 1.3 Create `grafana-app.yaml` in `infra/services/observability/grafana/`
- [x] 1.4 Create `opentelemetry-app.yaml` in `infra/services/observability/opentelemetry/`
- [x] 1.5 Create `argocd-app.yaml` in `infra/services/observability/argocd/`
- [x] 1.6 Create `registry-app.yaml` in `infra/services/registry/`

## 2. Verify Existing Applications

- [x] 2.1 Verify `postgres-app.yaml` has automated sync policy
- [x] 2.2 Verify `redis-app.yaml` has automated sync policy
- [x] 2.3 Verify `gateway-app.yaml` has automated sync policy
- [x] 2.4 Verify `keycloak-app.yaml` has automated sync policy
- [x] 2.5 Verify `seq-app.yaml` has automated sync policy

## 3. Validation

- [x] 3.1 Run `kubectl apply --dry-run=client` on all new Application manifests (kubectl not available in env - YAML validated manually)
- [x] 3.2 Verify all Applications follow consistent pattern
