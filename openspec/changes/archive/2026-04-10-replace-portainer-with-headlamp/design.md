## Context

Currently the cluster uses Portainer (`portainer.infra.svc.cluster.local:9000`) as a web-based dashboard for cluster management. Portainer is being deprecated in favor of Headlamp, a modern Kubernetes-native dashboard maintained by the Kubernetes SIG-UI.

## Goals / Non-Goals

**Goals:**
- Replace Portainer with Headlamp as the cluster management dashboard
- Maintain the same ingress URL pattern (`headlamp.mydomain.com`)
- Use the `infra` namespace for consistency with other services
- Configure Headlamp with in-cluster mode for direct Kubernetes API access

**Non-Goals:**
- Migrating Portainer data/configuration (fresh install)
- Adding OIDC authentication (use simple token-based auth)
- Enabling Helm plugin capabilities in Headlamp

## Decisions

1. **Namespace**: Use `infra` namespace instead of `kube-system` to match other platform services
   - Alternative: Use `kube-system` (like the official manifests) - Rejected: Inconsistent with project structure

2. **Deployment approach**: Plain Kubernetes manifests instead of Helm chart
   - Alternative: Use official Helm chart - Rejected: Keeping with the existing pattern of plain YAML manifests in this repo

3. **Image**: Use `ghcr.io/headlamp-k8s/headlamp:latest` from the official registry
   - Alternative: Pin specific version - Rejected: Latest follows the existing pattern for other images in this repo

4. **Service type**: ClusterIP with nginx ingress (existing pattern)
   - Alternative: LoadBalancer - Rejected: Using existing ingress infrastructure

5. **No PVC needed**: Headlamp doesn't require persistent storage by default
   - Alternative: Add PVC for plugins - Not needed for basic functionality

## Risks / Trade-offs

- **Risk**: Headlamp requires cluster-wide RBAC for full functionality
  - **Mitigation**: Create a ClusterRole with read-only access or cluster-admin (for admin dashboard use)

- **Risk**: Authentication method differences
  - **Mitigation**: Use the built-in token-based auth with a service account

## Migration Plan

1. Delete Portainer resources:
   - Delete `infra/services/observability/portainer/` directory
   - Remove Portainer references from README.md

2. Create Headlamp resources:
   - Create `infra/services/observability/headlamp/` directory
   - Add deployment.yaml, service.yaml, app.yaml, ingressroute.yaml
   - Create ClusterRole and ServiceAccount for RBAC

3. Update README.md:
   - Replace Portainer entries with Headlamp entries
   - Update DNS documentation

4. Deploy and verify:
   - ArgoCD will sync the new application
   - Access via `headlamp.mydomain.com`