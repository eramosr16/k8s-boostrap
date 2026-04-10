## Context

The cluster currently has Seq deployed in `infra/services/observability/seq/` for log aggregation, requiring its own PostgreSQL backend. Grafana is already deployed for metrics visualization and supports Loki natively as a datasource. Having both Seq and Loki creates redundant infrastructure on a single server.

## Goals / Non-Goals

**Goals:**
- Replace Seq with Loki for unified metrics + logs in Grafana
- Deploy Promtail as DaemonSet to collect all K8s pod logs
- Remove Seq and its PostgreSQL dependency
- Update config.yaml and documentation

**Non-Goals:**
- Migrate existing Seq logs (fresh start with Loki)
- Change application logging format (Serilog remains)
- Add distributed tracing (future work)

## Decisions

### 1. Loki over Elasticsearch
**Decision:** Use Loki instead of Elasticsearch for log aggregation.

**Rationale:**
- Native Grafana integration (same UI for metrics + logs)
- Lower resource usage (~500MB vs 2GB+ for ES)
- Indexes metadata only, not full text (cheaper storage)
- Simpler deployment (single binary, no Lucene complexity)

**Alternatives considered:**
- Elasticsearch: More powerful search, but heavier resources
- ClickHouse: Excellent for high-volume logs, but more complex setup

### 2. Promtail as log shipper
**Decision:** Use Promtail as DaemonSet to collect K8s pod logs.

**Rationale:**
- Official Loki log shipper, well-integrated
- Runs as DaemonSet - one per node, minimal overhead
- Supports file-based collection and Kubernetes metadata labels
- Can tail stdout/stderr directly from pods

**Alternatives considered:**
- Fluent Bit: More lightweight, but requires additional config
- Docker logging driver: Less flexible for filtering

### 3. Storage configuration
**Decision:** Use PVC with 10Gi storage for Loki.

**Rationale:**
- Single server = local storage
- 10Gi sufficient for 7-day retention on moderate log volume
- Can be adjusted via config.yaml if needed

### 4. Serilog integration for .NET applications
**Decision:** Recommend file output + Promtail tailing over direct HTTP.

**Rationale:**
- More resilient: app writes to file, Promtail handles delivery
- If Loki is down, app continues writing logs
- Kubernetes handles stdout/stderr natively

## Risks / Trade-offs

- **Risk:** Log query performance on large datasets
  - **Mitigation:** Loki's label-based indexing handles most queries efficiently; adjust retention if needed

- **Risk:** Application log ingestion requires file-based collection
  - **Mitigation:** Document Serilog configuration for file output; Promtail auto-discovers

- **Risk:** Breaking change for any services sending to Seq
  - **Mitigation:** Update application configs to send to Loki HTTP endpoint or use file output

## Migration Plan

1. **Add Loki manifests** to `infra/services/observability/loki/`
2. **Add Promtail manifests** to `infra/services/observability/promtail/`
3. **Update Grafana datasource** to include Loki
4. **Update config.yaml** - replace `seq` with `loki` image tag
5. **Remove Seq manifests** from `infra/services/observability/seq/`
6. **Update README.md** - change Seq references to Loki
7. **Update cluster diagram** - replace Seq with Loki
8. **Update run-all.sh** - remove Seq credential prompts

**Rollback:** Keep Seq manifests in git (can re-apply if needed); Loki can run alongside temporarily if needed for comparison.

## Open Questions

- **Q:** Should Loki be exposed externally for direct HTTP ingestion?
  - **A:** No - internal only; applications use file output + Promtail, or HTTP to `loki.infra.svc.cluster.local:3100`

- **Q:** What's the expected log volume for sizing?
  - **A:** Estimate ~1-2GB/day for moderate K8s cluster; 10Gi provides ~5-7 days retention