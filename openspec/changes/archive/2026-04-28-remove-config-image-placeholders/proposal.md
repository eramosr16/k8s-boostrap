## Why

The bootstrap flow currently stores image tags in `config.yaml` and then rewrites manifests by injecting those placeholders during `scripts/run-all.sh`. Those placeholders are out of sync with the GitOps manifests and cause ArgoCD to deploy services with invalid images, leading to crashes on first sync. Removing the placeholders from the config and letting the ArgoCD manifest define the images keeps the source of truth in one place while avoiding runtime substitution bugs.

## What Changes

- Remove the `images` block from `config.yaml` so that bootstrap configuration only contains cluster metadata, routes, and credentials.
- Eliminate the logic in `scripts/run-all.sh` that tries to replace image placeholders based on `config.yaml`; the script should rely entirely on the manifests pulled by ArgoCD for image tags.
- Document the new behavior in `README.md` and note that images must stay defined in the ArgoCD-managed manifests.

## Capabilities

### New Capabilities
- `config-image-cleanup`: Align bootstrap configuration with GitOps manifests by removing image overrides and the associated script logic.

### Modified Capabilities
- *None.*

## Impact

- `config.yaml` (cluster metadata) will have its `images` section removed.
- `scripts/run-all.sh` will no longer read or act on image tags from `config.yaml`.
- `README.md` will gain a short note explaining that image tags must live in the application manifests so duplicate overrides do not cause failures.

## Non-goals

- Touching the ArgoCD application manifests or moving image tags elsewhere in the repository.
- Adding new scripting around image promotion or version pinning; the change just stops the bootstrap from overwriting what ArgoCD already deploys.
