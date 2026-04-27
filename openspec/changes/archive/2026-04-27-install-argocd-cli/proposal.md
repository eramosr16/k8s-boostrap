## Why

`run-all.sh` currently assumes the `argocd` CLI is available when diagnosing sync issues, but freshly bootstrapped systems (as demonstrated by the missing CLI on Debian) can’t run `argocd app ...` commands. That makes troubleshooting harder and prevents operators from verifying deployments during bootstrap.

## What Changes

- Ensure the bootstrap script installs the `argocd` CLI when it is absent so all subsequent automation (health checks, app inspection) can run without manual CLI setup.
- Verify the download matches the platform architecture, makes the binary executable, and places it in a directory on `PATH` (falling back to `sudo` if needed).
- Document in `README.md` that the script now installs the CLI automatically and operators can skip manual installation.

## Capabilities

### New Capabilities
- `argocd-cli-installation`: Guarantee the ArgoCD CLI is installed on bootstrap systems so diagnostics and future automation can rely on the CLI being available.

### Modified Capabilities
- _None_

## Impact

- `scripts/run-all.sh` gains a new helper to download, verify, and install the `argocd` CLI before the script attempts to inspect ArgoCD applications.
- The bootstrap documentation (README) must describe the new behavior so operators understand the CLI requirement is handled automatically.
- Users with custom installation paths may need to re-run the script if they prefer a different `argocd` binary location.

## Non-goals

- Replacing the CLI download with a packaged distribution (this remains a script-level convenience).
- Supporting every platform the ArgoCD team publishes binaries for (we focus on Linux/x86-64 for bootstrap hosts).
