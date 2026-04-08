# K8s Cluster Manifests

This repo defines a K8s cluster deployed via ArgoCD.

## Directories

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

## Scripts

Bootstrap local K3s cluster:
```bash
./scripts/bootstrap.sh
```

Install ArgoCD:
```bash
./scripts/install-argocd.sh
```

## OpenSpec

This repo uses OpenSpec for structured change management. Changes are stored in `openspec/changes/`.
- Use `opencode` with the `openspec-*` skills for feature work
- Archive changes before cleanup: `skill openspec-archive-change`