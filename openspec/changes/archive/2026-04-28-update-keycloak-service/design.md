## Context

- The current Keycloak deployment under `infra/services/iam/keycloak` uses `quay.io/keycloak/keycloak:26.6` with manual `--db` args, JDBC URL pointing at `postgres`, and multiple `KC_*` environment variables.
- ArgoCD manages these manifests and we already have secrets (e.g., `keycloak-secret`) delivering the admin password and database password.
- The goal is to consolidate the manifest into the Bitnami distribution so ArgoCD can deploy a self-contained, patched image without manual multi-step tweaks.

## Goals / Non-Goals

**Goals:**

- Replace the deployment image with `docker.io/bitnami/keycloak:latest`, keep port 8080 exposed, and supply the PostgreSQL host/name/user environment variables that the Bitnami image authors expect.
- Keep the existing secrets-backed credentials for the admin user and the database password so no new secret material is introduced.
- Document the change (README entry) so operators know the IAM stack now uses the Bitnami runtime.

**Non-Goals:**

- Modifying Keycloak realms, clients, or other identity artifacts.
- Changing the PostgreSQL database host, schema, or credentials beyond what the current manifest already references.
- Rewriting bootstrap scripts or other services that do not depend on the Keycloak image.

## Decisions

- Use the Bitnami-provided image in `docker.io/bitnami/keycloak:latest` because it bundles all necessary server configuration, database drivers, and the `KEYCLOAK_*` env schema that avoids the two-step updater required by the older `quay.io` flavor.
- Retain the current service ports and ArgoCD application so the Helm-style upgrade is limited to the deployment manifest under `infra/services/iam/keycloak`.
- Map the required env vars (`KEYCLOAK_DATABASE_HOST`, `KEYCLOAK_DATABASE_NAME`, `KEYCLOAK_DATABASE_USER`) to the existing PostgreSQL service (`postgresql`) so the migration does not require new DNS entries.
- Continue using the existing `keycloak-secret` for the admin password and database password rather than introducing plaintext values.

## Risks / Trade-offs

- [Image drift] Bitnami’s `latest` tag may roll out breaking changes; mitigation is to stage the change in dev and, if volatility is observed, pin to a specific digest or release in a follow-on task.
- [Env mismatch] The Bitnami image expects slightly different env names than the current downstream image; mitigation is to test the manifest locally with `kubectl apply --dry-run=client` and inspect the generated pods for readiness.
- [Service disruption] Rolling the deployment will briefly restart Keycloak pods; if any preexisting sessions rely on persistence, we can rely on the existing database and secrets to make the transition seamless.

## Migration Plan

1. Update `infra/services/iam/keycloak/keycloak-deployment.yaml` to remove the extra `start` args and KC_* env vars, replacing them with the Bitnami image plus `KEYCLOAK_DATABASE_*` entries.
2. Keep the service, ingress, and ArgoCD application unchanged so that ArgoCD simply syncs the modified manifest.
3. Once committed, let ArgoCD reconcile the new image; monitor the Keycloak pod logs to confirm the Bitnami entrypoint successfully connects to `postgresql`.
4. If the deployment does not become ready, rollback by reapplying the previous manifest or revert the commit, then investigate the Bitnami logs before retrying.

## Open Questions

- Does the Bitnami image also expect `KEYCLOAK_DATABASE_PASSWORD`/`KEYCLOAK_ADMIN_PASSWORD` to come from the same secret, or should we inline those values temporarily during validation?
