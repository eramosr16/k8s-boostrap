## Context

K3s is currently installed using the default installer without any configuration options. Users who want to customize server settings (like disabling Traefik, changing the cluster CIDR, or enabling specific features) must modify their setup manually after installation. The goal is to provide a centralized configuration through `config.yaml` while maintaining K3s defaults as the fallback.

## Goals / Non-Goals

**Goals:**
- Add `k3s` section to `config.yaml` with default values matching K3s defaults
- Update `bootstrap.sh` to read K3s config from `config.yaml` and apply it during installation
- Provide sensible defaults that mirror K3s out-of-box behavior

**Non-Goals:**
- Agent node configuration (focus on server-only for now)
- Runtime configuration changes (containerd, etc.)
- HA/cluster mode (single-server default)

## Decisions

1. **Configuration structure**: Use simple key-value pairs in `config.yaml` under a `k3s` section
   - Alternative: Use a separate k3s config file - rejected, single source of truth preferred

2. **Default values**: Mirror K3s defaults (single server, Traefik enabled, etc.)
   - This ensures users starting with defaults get the same experience as before

3. **Installation method**: Pass K3s install flags via `INSTALL_K3S_EXEC` environment variable
   - Alternative: Use config file - more complex to manage

## Risks / Trade-offs

- **Risk**: Users may not realize K3s has configurable options
  - **Mitigation**: Document all available options in README.md

- **Risk**: Breaking existing bootstrap.sh for users without config.yaml
  - **Mitigation**: Make config.yaml optional, fall back to defaults if not present

- **Risk**: Some K3s options require restart to take effect
  - **Mitigation**: Document which options require reinstall vs. runtime apply