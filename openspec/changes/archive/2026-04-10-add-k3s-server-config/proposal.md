## Why

K3s by default creates a single server node, which works well for development and small deployments. However, users may want to customize this configuration (e.g., adding server nodes, enabling specific features) before bootstrapping the cluster. Currently, there's no centralized way to configure K3s server options - users must manually modify K3s installation flags each time.

## What Changes

- Add `k3s` configuration section to `config.yaml` with default values matching K3s defaults
- Add K3s server configuration to bootstrap script to read from `config.yaml`
- Document the available configuration options in README.md

## Capabilities

### New Capabilities
- `k3s-server-config`: K3s server configuration options in config.yaml

### Modified Capabilities
- None

## Impact

- New: `config.yaml` gains a `k3s` section with server options
- Modified: `scripts/bootstrap.sh` reads K3s config from config.yaml
- Modified: `README.md` documents K3s configuration options