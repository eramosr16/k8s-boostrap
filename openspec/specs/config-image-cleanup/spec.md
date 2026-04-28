## Purpose

Prevent the bootstrap configuration and script from keeping a separate copy of container image tags so the GitOps-managed manifests stay authoritative for service versions.

## Requirements

### Requirement: Config metadata excludes image tags
`config.yaml` SHALL only contain cluster metadata, routes, traefik settings, and service namespace configuration; it SHALL NOT define an `images` map or any per-service image tags.

#### Scenario: Config file review
- **WHEN** an operator inspects `config.yaml` after applying this change
- **THEN** they SHALL see entries for `cluster`, `k3s`, `traefik`, `routes`, and `services`, and SHALL NOT find an `images` section or any image tags

### Requirement: Bootstrap script relies on ArgoCD manifests for images
`scripts/run-all.sh` SHALL no longer read or substitute image tags into manifests based on `config.yaml`; it SHALL rely on the GitOps-managed manifests pulled by ArgoCD for all image references.

#### Scenario: Script execution
- **WHEN** the operator runs `./scripts/run-all.sh` with a cleaned `config.yaml`
- **THEN** the script SHALL skip any image substitution logic and proceed to apply `boostrap/root-app.yaml` without warning about missing image tags

### Requirement: Documentation states image defaults live in application manifests
`README.md` SHALL state that image tags are defined in the ArgoCD-managed manifests, and operators SHALL not expect to override them through `config.yaml`.

#### Scenario: README review
- **WHEN** an operator reads the README after this change
- **THEN** they SHALL see a short note explaining that image versions are managed in the manifests and are not configurable via `config.yaml`
