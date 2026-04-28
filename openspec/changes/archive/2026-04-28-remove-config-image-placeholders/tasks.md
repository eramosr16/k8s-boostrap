## 1. Config cleanup

- [x] 1.1 Remove the `images` map from `config.yaml` so it only contains cluster metadata, routes, and service namespace info
- [x] 1.2 Update the README quick start/config sections to explain that image tags live in the ArgoCD manifests and are no longer configurable via `config.yaml`

## 2. Script maintenance

- [x] 2.1 Strip the image substitution logic from `scripts/run-all.sh`, ensuring it no longer reads `images` from `config.yaml`
- [x] 2.2 Confirm the bootstrap flow still applies `boostrap/root-app.yaml` and handles traefik templating without touching image tags
