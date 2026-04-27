## 1. Setup tooling

- [x] 1.1 Add an `install_argocd_cli()` helper that downloads the correct release binary and installs it to `/usr/local/bin/argocd` (with `sudo` if needed).
- [x] 1.2 Ensure the helper runs near the start of `main()` so downstream steps can assume `argocd` exists.

## 2. Documentation & validation

- [x] 2.1 Update `README.md` to mention the bootstrap script now manages the ArgoCD CLI.
- [x] 2.2 Validate the new helper works on a Linux host by simulating a missing CLI (e.g., uninstalling or renaming existing `argocd`).
