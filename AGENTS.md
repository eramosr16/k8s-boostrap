# K8s Cluster Manifests

Work in `/home/ernesto/Repository/Cluster/k8s`. This repo defines a K8s cluster deployed via ArgoCD.

## Directories

- `bootstrap/` - Initial bootstrap (root-app watches `/apps`)
- `infra/services/` - Platform services (databases, broker, gateway, observability)
- `infra/applications/` - User-facing applications

## Adding resources

Add YAML manifests to the appropriate directory under `services/` or `applications/`. Follow the structure in `Readme.md`.

## Commands

Validate YAML syntax:
```bash
kubectl apply --dry-run=client -f <file>.yaml
```

Check ArgoCD sync status (run on cluster):
```bash
argocd app get <app-name>
```