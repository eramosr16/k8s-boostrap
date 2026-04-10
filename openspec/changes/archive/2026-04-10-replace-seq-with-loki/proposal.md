## Why

The cluster currently has both Seq and Loki for log aggregation. This is redundant - Seq requires its own UI and PostgreSQL backend, while Loki integrates natively with Grafana (already deployed). For a single-server resource-constrained environment, keeping both adds unnecessary CPU, memory, and storage overhead.

## What Changes

- Remove Seq service from `infra/services/observability/seq/`
- Add Loki to `infra/services/observability/loki/`
- Add Promtail as DaemonSet to collect K8s pod logs
- Add Loki as Grafana datasource
- Update `config.yaml` to use Loki instead of Seq
- Update `README.md` to reflect Loki as the log aggregation solution
- Update cluster diagram to show Loki instead of Seq

## Capabilities

### New Capabilities
- `loki-stack`: Horizontal-scalable log aggregation system replacing Seq
- `promtail-agent`: Log shipper running as DaemonSet to collect all K8s pod logs

### Modified Capabilities
- `grafana-visualization`: Add Loki as datasource (already exists, will update)
- `seq-service`: Mark as deprecated/removed

## Impact

- Reduces memory footprint by ~1.5GB (Seq + PostgreSQL backend vs Loki)
- Single UI for metrics and logs in Grafana
- Simpler architecture - no separate log aggregation server
- Application logs still supported via file output + Promtail
- Breaking: Any existing Seq ingest URLs need to update to Loki

## Non-Goals

- Add distributed tracing (separate concern)
- Migrate existing Seq logs (Seq will be removed, fresh start with Loki)
- Change application logging format (apps continue using Serilog)