## Why

Currently the ArgoCD bootstrap root-app only watches the `apps` directory. The `infra/` folder contains platform services (databases, broker, gateway, observability) and user-facing applications that need to be deployed to the cluster but are not being watched by the root application.

## What Changes

- Update the ArgoCD root-app.yaml to watch the `infra/` directory instead of or in addition to `apps`
- The root-app will deploy all YAML manifests under `infra/services/` and `infra/applications/`
- This enables automatic deployment of all platform services and applications via ArgoCD

## Capabilities

### New Capabilities
- `argocd-root-app-infra`: Define an ArgoCD Application resource that watches the `infra/` directory and recursively deploys all contained YAML manifests to the cluster

### Modified Capabilities
- None

## Impact

- ArgoCD root application manifest (`bootstrap/root-app.yaml`)
- All manifests under `infra/services/` and `infra/applications/` will be automatically deployed when added to the cluster