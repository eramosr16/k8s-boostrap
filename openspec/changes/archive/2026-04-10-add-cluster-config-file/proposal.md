## Why

Currently, non-sensitive configuration values like cluster domain, Traefik email, and Docker image tags are hardcoded across multiple YAML manifests. This makes it error-prone to update these values manually and difficult to bootstrap a new environment. Creating a centralized config file allows users to configure all these values once before running the bootstrap script.

## What Changes

- Create `config.yaml` in repository root with configurable non-sensitive values
- Update `run-all.sh` to read config file and apply values as placeholders in manifests before deployment
- Ensure config file follows YAML best practices with sensible defaults

## Capabilities

### New Capabilities

- `cluster-config`: Centralized configuration file for non-sensitive cluster values including cluster domain, Traefik email, and Docker image tags

## Impact

- New file: `config.yaml` in repository root
- Modified: `scripts/run-all.sh` to read config and template manifests