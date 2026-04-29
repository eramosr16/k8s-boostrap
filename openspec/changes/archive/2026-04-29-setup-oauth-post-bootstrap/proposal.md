## Why

Running `scripts/run-all.sh` can fail halfway when Keycloak or PostgreSQL are unavailable, leaving the realm, clients, and secrets only partially configured. That blocks the rest of the platform from authenticating and requires rerunning the entire bootstrap pipeline, which repeats credential prompts and can leave duplicate resources. We need a standalone way to finish OAuth setup once the cluster is healthy.

## What Changes

- Introduce a focused script under `scripts/` that configures the Keycloak infra realm, clients for Grafana/ArgoCD/Headlamp, and the related Kubernetes secrets only after the cluster is reachable.
- Document how to run this script manually after the bootstrap dependencies are restored so operators can retry OAuth configuration without re-running the full bootstrap.
- Ensure the script is idempotent and logs clear status so operators can tell whether each service received its OAuth config.

## Capabilities

### New Capabilities
- `oauth-service-on-demand`: Scripts and docs that let operators reapply the Keycloak realm, clients, and service secrets after the cluster is already running. It encapsulates the post-bootstrapping OAuth setup so the services depending on Keycloak can be brought back to a healthy state without replaying the entire bootstrap.

### Modified Capabilities
- None

## Impact

- Add `scripts/setup-oauth-after-bootstrap.sh` (or the chosen name) and ensure it only targets Keycloak, Grafana, ArgoCD, and Headlamp clients/secrets.
- Update docs so the recovery path is discoverable, including references in the repository README.
- No changes to existing ArgoCD manifests, but the new script will rely on cluster services already being up.

## Non-goals

- Don’t attempt to re-run K3s, ArgoCD, or secret bootstrapping steps beyond the OAuth context (secrets should already exist).
- No mass reconfiguration of Keycloak beyond the specific clients that serve Grafana, ArgoCD, and Headlamp.
