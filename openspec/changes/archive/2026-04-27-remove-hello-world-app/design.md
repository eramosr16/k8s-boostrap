## Context

The `hello-world` application under `infra/applications` serves no production purpose, yet it still exists in the repository and is watched by the ArgoCD root app. Keeping it in the repo adds noise to the GitOps tree and slightly delays syncs.

## Goals / Non-Goals

**Goals:**
- Delete the `hello-world` app manifest directory and ensure no ArgoCD application or documentation references remain.
- Keep the ArgoCD workspace clean by updating root application manifests so the deletion does not cause deployment errors.
- Document the removal in the README so operators understand why the app is no longer present.

**Non-Goals:**
- Replacing the hello-world app with another sample application.
- Modifying unrelated applications or infrastructure unless they explicitly reference the hello-world app.

## Decisions

- **Directory removal:** We delete the entire `infra/applications/hello-world` directory rather than extracting parts or moving it elsewhere because it only hosts a simple placeholder app that is no longer used.
- **ArgoCD cleanup:** Remove the `hello-world` application entry from any ArgoCD manifests (likely under `infra/applications` or the bootstrapped root app) instead of keeping a disabled stub; this prevents sync failures after the directory is gone.
- **Documentation update:** Add a short note in `README.md` and relevant change logs explaining that the app is removed so future maintainers understand the intent.

## Risks / Trade-offs

- **[ArgoCD sync errors]** Removing the directory before updating manifests could break sync. → Update ArgoCD manifests first, then delete the directory in the same commit to keep the tree consistent.
- **[Loss of history]** The hello-world app may contain references someone still relies on. → Preserve the directory in git history; mention in README and specs that the app was removed intentionally.

## Migration Plan

1. Update ArgoCD root application manifests to drop the `hello-world` application reference.
2. Delete `infra/applications/hello-world` and any related kube manifests that are no longer referenced.
3. Update documentation (README/recent updates) explaining the removal for future reference.
4. Validate the repo by ensuring `kubectl apply --dry-run` still succeeds for remaining apps and root app manifests reference valid directories.

## Open Questions

- None.
