## Context

- The Camunda/Bitnami Keycloak image now expects `KC_BOOTSTRAP_ADMIN_USERNAME` and `KC_BOOTSTRAP_ADMIN_PASSWORD` instead of the legacy `KEYCLOAK_ADMIN_USER` and `KEYCLOAK_ADMIN_PASSWORD`. Without the KC-prefixed vars the bootstrap admin account is never created.
- Our deployment currently wires `KEYCLOAK_ADMIN_*` env vars and the bootstrap secret (`keycloak-secret`) stores `KEYCLOAK_ADMIN_PASSWORD`. The optimized image logs the absence of the KC variables every time it starts.
- `scripts/run-all.sh` already writes `KC_BOOTSTRAP_ADMIN_PASSWORD` for compatibility, but the manifest and README/reference still only mention `KEYCLOAK_*` names, so automation and operators can be out of sync.

## Goals / Non-Goals

**Goals:**

- Update `infra/services/iam/keycloak/keycloak-deployment.yaml` to export the KC- prefixed bootstrap env vars sourced from `keycloak-secret` so the admin user creation succeeds.
- Ensure `scripts/run-all.sh` writes both `KC_BOOTSTRAP_ADMIN_USERNAME` and `KC_BOOTSTRAP_ADMIN_PASSWORD` and update README so the intended env var names are documented for secret rotation.

**Non-Goals:**

- Introducing new secrets beyond Keycloak’s credentials.
- Changing keycloak service ports, database connectivity, or the bootstrap username value (`admin`).

## Decisions

- Use `keycloak-secret` with the `KC_BOOTSTRAP_ADMIN_PASSWORD` key and keep `KEYCLOAK_DATABASE_PASSWORD` for database connectivity so we do not duplicate secrets.
- Keep the bootstrap username hardcoded to `admin` inside the manifest to match existing expectations and avoid requiring a new environment variable.
- Document the required env var tuple (`KC_BOOTSTRAP_ADMIN_USERNAME`, `KC_BOOTSTRAP_ADMIN_PASSWORD`) in README so future maintainers recreate the secret correctly.

## Risks / Trade-offs

- [Secret mismatch] If automation still writes to `KEYCLOAK_ADMIN_PASSWORD` only, the manifest will not find `KC_BOOTSTRAP_ADMIN_PASSWORD`; mitigation: update the script and README and communicate the needed key names.
- [Restarts] Changing env vars requires ArgoCD to reapply the deployment, which will briefly restart Keycloak pods; mitigation: schedule the rollout during maintenance windows if needed.

## Migration Plan

1. Update the deployment manifest env section to declare `KC_BOOTSTRAP_ADMIN_USERNAME` and `KC_BOOTSTRAP_ADMIN_PASSWORD`, removing the old `KEYCLOAK_ADMIN_*` entries. Make sure `KEYCLOAK_DATABASE_*` vars remain untouched.
2. Adjust `scripts/run-all.sh` to keep writing `KC_BOOTSTRAP_ADMIN_USERNAME` and `KC_BOOTSTRAP_ADMIN_PASSWORD` into `keycloak-secret` alongside the database password.
3. Update README to mention the KC bootstrap env names so operator documentation matches the implementation.

## Open Questions

- Should we remove the old `KEYCLOAK_ADMIN_PASSWORD` entry from `keycloak-secret` or keep it for backward compatibility once all tooling is updated?
