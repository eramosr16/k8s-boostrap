## Context

Bootstrapping the cluster currently relies on `config.yaml` not just for domain metadata but also for image tags. The `scripts/run-all.sh` script loads that file and rewrites placeholders so the ArgoCD applications pick up the configured tags. When the placeholders are left empty (for example, because the script is run without editing `config.yaml`), ArgoCD pulls manifests with literal placeholders such as `<grafana-image>` and the services crash. ArgoCD already tracks the correct image tags in the GitOps repo, so forcing the bootstrap script to rewrite them is redundant and fragile.

## Goals / Non-Goals

**Goals:**

- Limit `config.yaml` to cluster metadata, routes, and non-sensitive values so it cannot accidentally break manifests.
- Remove the run-time substitution logic in `scripts/run-all.sh` that reads `images` from `config.yaml`.
- Make it clear in `README.md` that image tags belong in the GitOps manifests, and that the bootstrap runner will no longer change them.

**Non-Goals:**

- Modifying any ArgoCD manifest or gitops application to move images elsewhere.
- Adding a new configuration layer for managing image versions; this change only removes duplicate overrides.

## Decisions

- Keep image tags defined in the ArgoCD-managed manifests instead of a separate config file because the manifests are already the source of truth and removing the extra layer avoids synchronization issues.
- Strip the `images` section from `config.yaml` and the associated substitution logic so `scripts/run-all.sh` only uses the config for metadata it already trusted (domains, routes, secrets). This simplifies the script and reduces the chance of injecting invalid placeholders into ArgoCD syncs.
- Document the updated behaviour in `README.md` so future operators know not to expect image overrides in `config.yaml`.

## Risks / Trade-offs

- [Risk] Operators may expect image override fields when running `run-all.sh`; without them, the script no longer warns or defaults on missing versions. → Mitigation: the README will call out that images live in the GitOps manifests, and existing manifests already specify pinned tags.
- [Risk] If the GitOps manifests ever remove their image tags, there is no backup override. → Mitigation: keep manifest image tags pinned and update the GitOps repo as needed; this change merely removes redundant overrides from the bootstrap config.

## Migration Plan

1. Remove the `images` section from `config.yaml` and update documentation so users stop editing or expecting it.
2. Update `scripts/run-all.sh` to drop any logic that reads or replaces image placeholders; the script should be rerun with the cleaned config (no additional cluster changes needed).
3. Commit the change so ArgoCD syncs pull the correct images directly from the manifests once the bootstrap reruns.

## Open Questions

- None.
