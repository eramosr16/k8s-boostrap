## Context

The k8s-bootstrap project uses ArgoCD to manage Kubernetes manifests. It already includes PostgreSQL and Redis services. RabbitMQ is referenced in the README directory structure but hasn't been implemented yet.

## Goals / Non-Goals

**Goals:**
- Deploy RabbitMQ as a Kubernetes Deployment in the `infra` namespace
- Provide internal ClusterIP service for other apps to connect
- Use PersistentVolumeClaim for message persistence
- Store credentials in Kubernetes Secret with placeholder values

**Non-Goals:**
- High-availability clustering (single node)
- Exposing management UI externally
- Pre-configured exchanges/queues/vhosts

## Decisions

1. **Image**: Use official `rabbitmq:3-management` which includes the management UI (useful for debugging)
2. **Storage**: Use emptyDir for simplicity (can be upgraded to PVC later)
3. **Credentials**: Use Kubernetes Secret with RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS
4. **Namespace**: Deploy in `infra` namespace (consistent with postgres/redis)

## Risks / Trade-offs

- [Risk] Data loss on pod restart → [Mitigation] Add PVC for persistence
- [Risk] Default credentials in source control → [Mitigation] Use env var placeholders, require override before production
- [Risk] No resource limits → [Mitigation] Add requests/limits in deployment

## Migration Plan

1. Apply secret manifest (set password via env var)
2. Apply deployment + service
3. Verify pod starts and service is reachable
4. Update README with connection details