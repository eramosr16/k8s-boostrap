## ADDED Requirements

### Requirement: Bootstrap script installs argocd CLI when missing
The bootstrap process SHALL detect if `argocd` is missing, download the pinned release binary for the host architecture, make it executable, and place it in `/usr/local/bin` (using `sudo` when needed), so CLI commands used later in the script succeed without manual intervention.

#### Scenario: CLI installed by bootstrap
- **WHEN** `argocd` is not available on a fresh host and `./scripts/run-all.sh` runs
- **THEN** the script downloads the configured `ARGOCD_CLI_VERSION`, installs it to `/usr/local/bin/argocd`, and subsequent `argocd` invocations succeed

### Requirement: Download respects architecture and retries
The installation SHALL select the binary variant matching `uname -m` (e.g., `amd64` for `x86_64`) and fail fast with a descriptive error if the download cannot be retrieved after retries.

#### Scenario: Retry download logic
- **WHEN** the download fails temporarily (network or GitHub rate limit)
- **THEN** the script retries the download a couple of times and logs a clear error message if all attempts fail

### Requirement: Script documents CLI installation behaviour
Documentation SHALL explain that `scripts/run-all.sh` installs the `argocd` CLI automatically, so operators do not need to pre-install it themselves.

#### Scenario: README mentions CLI handling
- **WHEN** a user reads the bootstrap README after the change
- **THEN** there is a recent update describing that the script now provisions the ArgoCD CLI and maintains it in `/usr/local/bin`
