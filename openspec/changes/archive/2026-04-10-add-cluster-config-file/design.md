## Context

Currently, values like `LETS_ENCRYPT_EMAIL`, `cluster.local`, and Docker image tags are hardcoded in YAML manifests. When users run `run-all.sh`, they must manually edit these files or enter values interactively. A centralized config file would allow users to configure everything upfront.

## Goals / Non-Goals

**Goals:**
- Provide a single `config.yaml` file with all non-sensitive configuration
- Allow `run-all.sh` to read config and template manifests before applying
- Keep sensitive data (passwords, keys) in secrets or environment variables

**Non-Goals:**
- Store sensitive data in config.yaml (passwords, API keys remain in run-all.sh prompts)
- Replace existing secret manifests - only update placeholders

## Decisions

1. **Config file location**: Root `config.yaml` - simple and discoverable
2. **Format**: YAML with clear sections - follows k8s conventions
3. **Template mechanism**: `run-all.sh` uses `envsubst` or sed to replace placeholders in manifests with values from config
4. **Default values**: sensible defaults provided for development
5. **No new dependencies**: Uses bash builtins only

## Risks / Trade-offs

- [Risk] Users modifying config after initial setup → Document that config should be set before running run-all.sh
- [Risk] Template placeholder conflicts → Use distinctive placeholders like `{{CLUSTER_DOMAIN}}` to avoid conflicts

## Migration Plan

1. Create `config.yaml` with all configurable values
2. Update `run-all.sh` to read config and apply values before deploying manifests
3. Document usage in README.md