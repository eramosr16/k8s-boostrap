## Context

- The Bitnami Keycloak image now expects `KEYCLOAK_BOOTSTRAP_ADMIN_USERNAME` and `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` instead of the legacy `KEYCLOAK_ADMIN`/`KEYCLOAK_ADMIN_PASSWORD` vars for enabling bootstrap.
- Our deployment already sources `KEYCLOAK_ADMIN_PASSWORD` and `KEYCLOAK_ADMIN` from `keycloak-secret`, but the new runtime refuses to finish bootstrap when those names are missing.
- The secret has the `KEYCLOAK_ADMIN_PASSWORD` key today; we need to align the secret and the manifest with the Bitnami naming while reusing existing credentials.

## Goals / Non-Goals

**Goals:**

- Update the Keycloak Deployment manifest to export `KEYCLOAK_BOOTSTRAP_ADMIN_USERNAME`/`KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD`, keeping the same secret-backed passwords so bootstrap succeeds without new plaintext secrets.
- Document the required variable names so future rollouts provide the correct keys in `keycloak-secret` and automation remains consistent.

**Non-Goals:**

- Reworking Keycloak realms, clients, or login flows.
- Changing database connectivity or port/service names beyond the env vars already discussed.

## Decisions

- Use the existing `keycloak-secret` to source the password (rename the key to `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` via secret updates if necessary) so no duplicate secret is created.
- Keep the service and deployment definitions unchanged except for the env vars to minimize ArgoCD churn and avoid service restarts.
- Log the expected variable names in README so operators know to update secrets when rotating passwords.

## Risks / Trade-offs

- [Secret rename] If we rename the key inside `keycloak-secret`, any automation that sets `KEYCLOAK_ADMIN_PASSWORD` must also update; mitigation: include instructions in README and keep both keys temporarily if needed.
- [Bootstrap failure] Typo or mismatch in env names would break admin setup; mitigation: run `kubectl apply --dry-run=client` and watch pod logs after deployment.

## Migration Plan

1. Update `infra/services/iam/keycloak/keycloak-deployment.yaml` env section to export the bootstrap names alongside the database env vars.
2. Verify the `keycloak-secret` contains `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` and optionally update it, then ensure the deployment references that key.
3. Document the required secret contents in README and notify operators of the change.

## Open Questions

- Should we keep the old `KEYCLOAK_ADMIN` env var for backward compatibility or remove it entirely once the Bitnami image is confirmed stable?
