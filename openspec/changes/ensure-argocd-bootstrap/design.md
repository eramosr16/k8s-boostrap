## Context

Currently, the repository follows the App-of-Apps pattern where ArgoCD watches the `infra/` directory and deploys applications defined in it. However, not all service directories have ArgoCD Application manifests, leading to:

1. **Inconsistent deployment**: Only 5 services deploy automatically
2. **Manual intervention**: Services without Application manifests require manual `kubectl apply`
3. **No single source of truth**: Some services depend on external Application definitions

Current services in `infra/services/`:
- `databases/postgres` ✓ (has app)
- `databases/redis` ✓ (has app)
- `gateway` ✓ (has app)
- `iam/keycloak` ✓ (has app)
- `observability/seq` ✓ (has app)
- `broker/rabbitmq` ✗
- `observability/prometheus` ✗
- `observability/grafana` ✗
- `observability/opentelemetry` ✗
- `observability/argocd` ✗
- `registry` ✗

## Goals / Non-Goals

**Goals:**
- Create ArgoCD Application manifests for all services lacking them
- Ensure consistent naming convention: `<service>-app.yaml`
- Enable automatic GitOps deployment for the entire `infra/services/` directory

**Non-Goals:**
- Modifying deployment configurations (deployments, services, secrets)
- Changing the root-app.yaml (already watches `infra/` correctly)
- Adding new services
- Implementing complex sync policies beyond basic auto-sync

## Decisions

1. **Application manifest placement**: Each Application manifest will be placed in its service directory as `<service>-app.yaml` (e.g., `rabbitmq-app.yaml`)

2. **Naming convention**: 
   - Application name = directory name (e.g., `postgres`, `rabbitmq`, `prometheus`)
   - Namespace = `infra`
   - RepoURL = inherit from root-app or use `https://github.com/ernesto/k8s-boostrap.git`

3. **Sync policy**: Replicate existing pattern:
   ```yaml
   syncPolicy:
     automated:
       prune: true
       selfHeal: true
   ```

4. **Project**: All services use `default` project (matching existing pattern)

## Risks / Trade-offs

- **[Risk] Naming conflicts**: If service names duplicate existing Applications
  - **Mitigation**: Use directory-based names that don't conflict
- **[Risk] Large number of Applications**: May slow down ArgoCD sync
  - **Mitigation**: Enable ` prune: true` and `selfHeal: true` for quick convergence
- **[Risk] Missing dependencies**: Services may have startup dependencies (e.g., Keycloak needs PostgreSQL)
  - **Mitigation**: Document dependency order; ArgoCD handles some ordering natively

## Migration Plan

1. Create Application manifests for each missing service
2. Verify `kubectl apply --dry-run` passes for all new manifests
3. Push changes to git
4. ArgoCD will automatically detect and deploy new Applications
5. Verify all Applications sync to `Healthy` state
