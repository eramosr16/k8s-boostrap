## Context

The existing `scripts/run-all.sh` bootstraps everything once but aborts when Keycloak or PostgreSQL is unavailable. When that happens the Keycloak realm, clients, and service secrets only partially exist, leaving Grafana, ArgoCD, and Headlamp without OAuth configuration. Operators then re-run the whole script, which re-prompts for credentials and reruns unrelated steps. What we need is a focused, idempotent post-bootstrapping script that can configure the remaining OAuth pieces after the cluster is healthy.

## Goals / Non-Goals

**Goals:**

- Add a dedicated script (e.g., `scripts/setup-oauth-after-bootstrap.sh`) that ensures the Keycloak infra realm exists, bits the required clients, and syncs the Grafana, ArgoCD, and Headlamp secrets once the cluster is fully reachable.
- Keep the script customer-friendly: use existing secrets for credentials, log progress per service, and exit non-zero if Keycloak is unavailable so operators can retry safely.
- Document when and how to run that script so it becomes the standard retry path after a failed bootstrap.

**Non-Goals:**

- Re-running the entire bootstrap (K3s install, ArgoCD install, secret prompts) or touching services beyond Grafana/ArgoCD/Headlamp.
- Making configuration changes that would require ArgoCD reruns or spec updates unrelated to OAuth recovery.

## Decisions

1. **Separate OAuth recovery script** – Instead of bolting retry logic into `run-all.sh`, create `scripts/setup-oauth-after-bootstrap.sh` that assumes secrets already exist and only handles Keycloak realm/clients plus the related Kubernetes secrets. This keeps the bootstrap script lean and gives operators a clear recovery tool.
2. **Reuse existing credentials and kcadm** – The script will source `.env` or expect the same password variables as `run-all.sh`, then use `kubectl exec` into the Keycloak pod and run `kcadm` commands, mirroring the bootstrap behavior without re-provisioning other services.
3. **Target service-specific clients** – Focus on Grafana, ArgoCD, and Headlamp clients because they are the services that need OAuth secrets immediately after bootstrap. Each client creation step will be idempotent (`|| true` where needed) so the script can run repeatedly without error.
4. **Secret synchronization** – After ensuring the clients exist, retrieve the secrets via `kcadm get clients/.../client-secret` and update the corresponding Kubernetes secrets so services can pick up fresh credentials.

## Risks / Trade-offs

- [Keycloak still unavailable] → Script will fail fast if Keycloak pod isn’t ready; mitigate by waiting with timeouts before giving up.
- [Secrets drift] → If Grafana/ArgoCD secrets already have different credentials, overwriting them could break existing sessions; mitigate by logging warnings when overwriting and only updating the OIDC client secret fields.
- [Credential prompts still needed] → The script still requires env vars like `KEYCLOAK_ADMIN_PASSWORD`; document how to source them from `.env` so operators can run the script without re-typing values.

## Migration Plan

1. After the cluster and Keycloak/Postgres pods are healthy, run `KEYCLOAK_ADMIN_PASSWORD=<value> ./scripts/setup-oauth-after-bootstrap.sh` (or source `.env`).
2. The script will wait for the Keycloak health endpoint, recreate the `infra` realm/clients if missing, and refresh Grafana/ArgoCD/Headlamp secrets.
3. Once the script finishes successfully, verify Grafana/ArgoCD/Headlamp can authenticate via Keycloak and continue with any remaining manual checks.

## Open Questions

- Should the script also refresh Headlamp’s secrets or is the existing secret enough (only documented once)?
- Do we need to gate the script behind a flag in `run-all.sh` so it can be called automatically if Keycloak failed earlier?
