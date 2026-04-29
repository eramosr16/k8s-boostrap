# K8s Cluster Manifests

This repo defines a K8s cluster deployed via ArgoCD.

## Directories

- `infra/services/` - Platform services (databases, broker, gateway, observability)
- `infra/applications/` - User-facing applications

## Setup

This project uses Python with a virtual environment. Install dependencies:

```bash
make install
```

This will create a `.venv` virtual environment and install required packages from `requirements.txt`.

## Scripts

All scripts are now Python-based. Use the Makefile targets:

Bootstrap local K3s cluster:
```bash
make bootstrap
```

Install ArgoCD:
```bash
make install-argocd
```

Run full bootstrap process:
```bash
make run-all
```

Setup OAuth with Keycloak:
```bash
make setup-oauth
```

Verify container images:
```bash
make verify-images ARGS="--help"
```

Or run directly with the virtual environment:
```bash
.venv/bin/python scripts/bootstrap.py
```

## Commands

Validate YAML syntax:
```bash
kubectl apply --dry-run=client -f <file>.yaml
```

Check ArgoCD sync status (run on cluster):
```bash
argocd app get <app-name>
```

## OpenSpec

This repo uses OpenSpec for structured change management. Changes are stored in `openspec/changes/`.
- Use `opencode` with the `openspec-*` skills for feature work
- Archive changes before cleanup: `skill openspec-archive-change`