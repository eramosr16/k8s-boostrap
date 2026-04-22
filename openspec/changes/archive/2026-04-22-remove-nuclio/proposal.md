## Why

Nuclio serverless platform was added previously but is no longer needed for this infrastructure. Removing it simplifies the cluster, reduces resource usage, and eliminates maintenance overhead.

## What Changes

- Remove `nuclio` configuration from `config.yaml` (images.nuclio, routes.nuclio, nuclio section)
- Remove `nuclio` route loading from `scripts/run-all.sh`
- Remove `install_nuclio` function and all nuclio references from `scripts/run-all.sh`
- Remove `infra/services/nuclio/` directory and all its contents
- Keep the `infra/applications/` namespace (only remove nuclio-related content)

## Capabilities

### New Capabilities
None - this is a removal change only.

### Modified Capabilities
None - requirements are unchanged.

## Impact

- **Removed**: Nuclio namespace, helm chart, OAuth2 middleware, ingress routes
- **Modified**: config.yaml, scripts/run-all.sh
- **Affected Services**: None (serverless platform removed entirely)

## Non-goals

- Do not add any new services or capabilities
- Do not modify any other infrastructure services (PostgreSQL, Redis, Keycloak, etc.)