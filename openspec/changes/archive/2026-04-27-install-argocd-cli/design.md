## Context

During bootstrap we rely on the `argocd` CLI to inspect application health and, later, to perform cluster-level diagnostics. Fresh environments (like the Debian host above) typically lack the CLI, so operators must pause, install it manually, and re-run `run-all.sh`. This interrupts automation and makes the script less friendly in provisioning scenarios.

## Goals / Non-Goals

**Goals:**
- Install the `argocd` CLI automatically when missing so the bootstrap flow (and any subsequent troubleshooting commands) can run without manual setup.
- Keep the tooling limited to Linux/x86-64 hosts, which is the environment used for bootstrapping in this repo.
- Document the new behavior so operators know the script now manages the CLI.

**Non-Goals:**
- Providing cross-platform installers (macOS/Windows) for the CLI.
- Replacing existing package managers (e.g., `pip`, `brew`) that teams might prefer for their own setups.

## Decisions

- **Installation location:** Place the downloaded binary under `/usr/local/bin/argocd` (the standard path) and use `sudo` only if we lack write permissions. This keeps the CLI accessible to users without needing them to adjust `PATH`.
- **Version selection:** Default to a pinned release (e.g., `v2.9.11`) so the script does not suddenly break on upstream changes. Allow overrides via an environment variable (`ARGOCD_CLI_VERSION`) for future flexibility.
- **Download method:** Use `curl` with `-L` to follow redirects, download to a temporary file, mark it executable, and then move it into place. Validate the download by ensuring the file is non-empty.

## Risks / Trade-offs

- **[Download failure]** The GitHub release download could fail (network or rate limiting). → Wrap the download in a retry-friendly helper and fail with a clear message instructing the user to download manually.
- **[Permission issues]** Moving a binary into `/usr/local/bin` may require `sudo`. → Detect writability and use `sudo` automatically when needed.

## Migration Plan

1. Add a helper function `install_argocd_cli()` that downloads the CLI (if missing), makes it executable, and installs it to `/usr/local/bin` with optional `sudo`.
2. Call `install_argocd_cli()` before the script relies on the CLI (early in `main`) so that subsequent steps can execute `argocd` commands.
3. Update README to mention that the script manages the CLI installation, reducing manual prerequisites.

## Open Questions

- None.
