## Context

The ArgoCD bootstrap mechanism currently uses a root-app that watches an `apps` directory. However, the cluster configuration has an `infra/` directory containing platform services and applications under `infra/services/` and `infra/applications/`. These need to be deployed via ArgoCD but are not being watched by the root application.

## Goals / Non-Goals

**Goals:**
- Configure the ArgoCD root-app to watch and deploy all manifests under the `infra/` directory
- Enable automatic deployment of platform services (databases, broker, gateway, observability) and applications (hello-world, etc.)
- Use directory recursion to automatically pick up new manifests added to the infra folder

**Non-Goals:**
- Not modifying the existing bootstrap structure (root-app.yaml remains in bootstrap/)
- Not adding any new Kubernetes resources beyond the ArgoCD Application definition

## Decisions

1. **Watch `infra/` directory**: Changed the root-app source path from `apps` to `infra` to deploy all infrastructure manifests
2. **Use recursive directory scanning**: Enabled `recurse: true` to automatically discover all YAML manifests in subdirectories

## Risks / Trade-offs

- **Risk**: If there are YAML files that should NOT be deployed (e.g., templates, partials), they might get picked up by ArgoCD
  - **Mitigation**: Ensure only complete, valid Kubernetes manifests are placed in the infra directory

- **Risk**: Changing the watched directory might temporarily cause ArgoCD to show out-of-sync for existing resources
  - **Mitigation**: This is expected behavior; ArgoCD will reconcile and sync to the desired state