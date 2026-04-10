## Context

kube-score analysis revealed critical issues across all Kubernetes manifests in the cluster. The issues affect 10+ services including Loki, Promtail, PostgreSQL, Redis, RabbitMQ, Keycloak, Prometheus, Grafana, OpenTelemetry, and Headlamp.

## Goals / Non-Goals

**Goals:**
- Fix all kube-score CRITICAL issues
- Add security contexts to all workload manifests
- Ensure consistent image pull policy
- Fix Loki StatefulSet configuration

**Non-Goals:**
- Add NetworkPolicies (optional for single-node)
- Modify CPU/memory resource requests
- Change container images

## Decisions

### 1. Security Context Format
**Decision:** Use non-root security context for all containers.

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
```

**Rationale:** Follows Kubernetes security best practices. User ID 1000 is commonly used for container workloads.

### 2. Image Pull Policy
**Decision:** Set `imagePullPolicy: Always` for all containers.

**Rationale:** Ensures latest image is always pulled, prevents cached stale images.

### 3. Ephemeral Storage
**Decision:** Add ephemeral-storage limits (500Mi) to all containers.

**Rationale:** kube-score requires limits, 500Mi is reasonable for most workloads.

### 4. Probe Configuration
**Decision:** Use different ports for liveness vs readiness probes where needed.

**Rationale:** Using same port for both is flagged as dangerous by kube-score.

### 5. Loki ServiceName
**Decision:** Add `serviceName: loki` to Loki StatefulSet spec.

**Rationale:** Required by Kubernetes for StatefulSet networking.

## Risks / Trade-offs

- **Risk:** Some containers may not run as non-root (e.g., postgres)
  - **Mitigation:** Allow failures initially, adjust security context per service

## Migration Plan

1. Update each deployment/daemonset manifest with security context and image pull policy
2. Fix Loki StatefulSet serviceName
3. Re-run kube-score to verify fixes
4. ArgoCD will automatically sync changes

## Open Questions

- **Q:** Should NetworkPolicies be added despite being optional?
  - **A:** Not for single-node K3s, but document as future enhancement