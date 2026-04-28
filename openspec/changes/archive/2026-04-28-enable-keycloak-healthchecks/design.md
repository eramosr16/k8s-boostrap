## Context

- Keycloak uses the Bitnami/Camunda image, which disables `/health/*` endpoints unless explicitly enabled via `KC_HEALTH_ENABLED` and friends. Without them, Kubernetes readiness and liveness probes point at 8080 (which is not yet ready) and fail with connection refused.
- The bootstrap and manifest changes from prior work already keep the Postgres credentials aligned, so the final piece is to expose health endpoints and probe them correctly.

## Goals / Non-Goals

**Goals:**

- Enable `KC_HEALTH_ENABLED` plus `KC_HTTP_ENABLED` so the `/health` endpoints respond and reopen port 9000 for probes.
- Add `/health/live`, `/health/ready`, and `/health/started` probes on port 9000, mirroring the working deployment, so Kubernetes sees healthy pods before routing traffic.

**Non-Goals:**

- Changing Keycloak realms or authentication flows.
- Modifying database connectivity; the probes simply ensure the service stays reachable once the existing connection parameters succeed.

## Decisions

- Set `KC_PROXY_HEADERS=xforwarded` and `KC_HTTP_ENABLED=true` so the health endpoints are available through HTTP without HTTPS requiring TLS configuration.
- Add a container port 9000 exclusively for health to keep it separate from the public 8080 interface and match the upstream sample.
- Use HTTP probes with `/health/live` (liveness), `/health/ready` (readiness), and `/health/started` (startup) because they are lightweight and the image already exposes them once enabled.

## Risks / Trade-offs

- [Probe timing] Aggressive probes can cause early restarts; we mitigate by giving 120 seconds initial delay and using `/health/started` startup probes.
- [Dependency on env vars] If `KC_HEALTH_ENABLED` is removed, the probes will break again; the design includes documentation so future maintainers understand the dependency.
