## Why

The existing Keycloak service manifest currently relies on a two-step image patch so that the upstream deployment picks up the desired Bitnami runtime. Switching directly to the optimized `docker.io/bitnami/keycloak:latest` image removes that manual step, keeps the ArgoCD-managed manifest lean, and ensures every bootstrap gets a pre-configured, supported runtime.

## What Changes

- Replace `infra/services/iam/keycloak` with manifests that target `docker.io/bitnami/keycloak:latest`, expose port 8080, and include the standard Bitnami environment variables for PostgreSQL connectivity and the expected database schema.
- Update `README.md` to mention this change so future maintainers know the cluster now pins the Bitnami Keycloak image (per the repository guidance on documenting new changes).
- Verify that no other services depend on the legacy image configuration so ArgoCD can roll the new deployment without manual edits.

## Capabilities

### New Capabilities
- `keycloak-bitnami-image`: Align the `infra/services/iam/keycloak` manifests with the Bitnami Keycloak image and provide the PostgreSQL-related environment variables so the deployment becomes self-contained and ArgoCD-ready.

### Modified Capabilities
- `- None.`

## Impact

- `infra/services/iam/keycloak` (manifest files managed by ArgoCD)
- ArgoCD sync for the `iam` service group and any bootstrap tooling that relies on the old image template
- Keycloak consumers rely on the service staying on port 8080 and connecting to `postgresql` so we must keep those network expectations intact.

## Non-goals

- Introducing new realms, clients, or secrets for Keycloak
- Changing the database host, username, or schema name beyond what Bitnami expects
- Altering other IAM or application manifests unrelated to Keycloak
