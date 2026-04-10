## 1. Add Loki Service

- [x] 1.1 Create Loki StatefulSet manifest in `infra/services/observability/loki/loki-statefulset.yaml`
- [x] 1.2 Create Loki Service manifest in `infra/services/observability/loki/loki-service.yaml`
- [x] 1.3 Create Loki PVC manifest in `infra/services/observability/loki/loki-pvc.yaml`
- [x] 1.4 Create Loki ConfigMap manifest in `infra/services/observability/loki/loki-config.yaml`
- [x] 1.5 Create Loki ArgoCD Application manifest in `infra/services/observability/loki/loki-app.yaml`

## 2. Add Promtail Agent

- [x] 2.1 Create Promtail DaemonSet manifest in `infra/services/observability/promtail/promtail-daemonset.yaml`
- [x] 2.2 Create Promtail ConfigMap in `infra/services/observability/promtail/promtail-config.yaml`
- [x] 2.3 Create Promtail ServiceAccount in `infra/services/observability/promtail/promtail-serviceaccount.yaml`
- [x] 2.4 Create Promtail ClusterRole in `infra/services/observability/promtail/promtail-clusterrole.yaml`
- [x] 2.5 Create Promtail ClusterRoleBinding in `infra/services/observability/promtail/promtail-clusterrolebinding.yaml`
- [x] 2.6 Create Promtail ArgoCD Application manifest in `infra/services/observability/promtail/promtail-app.yaml`

## 3. Update Grafana Datasource

- [x] 3.1 Update Grafana datasource ConfigMap to include Loki in `infra/services/observability/grafana/grafana-datasource.yaml`

## 4. Update Configuration Files

- [x] 4.1 Update `config.yaml` - add loki image tag, remove seq
- [x] 4.2 Update `config.yaml` routes - change `seq: logs` to `loki: logs`

## 5. Update Documentation

- [x] 5.1 Update README.md - replace Seq references with Loki
- [x] 5.2 Update README.md service table - replace Seq with Loki
- [x] 5.3 Update README.md secrets table - remove Seq, add Loki if needed
- [x] 5.4 Update README.md folder structure - remove seq from observability
- [x] 5.5 Update cluster diagram in `docs/cluster-diagram.png` - replace Seq with Loki

## 6. Remove Seq Service

- [x] 6.1 Remove Seq deployment from `infra/services/observability/seq/`
- [x] 6.2 Remove Seq service from run-all.sh credential prompts

## 7. Update LinkedIn Post

- [x] 7.1 Update LinkedIn post to reference Loki instead of Seq (if previously posted)