## 1. Deployment updates

- [x] 1.1 Add `KC_HEALTH_ENABLED=true`, `KC_HTTP_ENABLED=true`, `KC_PROXY_HEADERS=xforwarded`, and `KC_METRICS_ENABLED=true` env vars to the Keycloak container so health endpoints become available.
- [x] 1.2 Declare container port 9000 and wire liveness/readiness/startup probes to `/health/live`, `/health/ready`, and `/health/started` on that port with conservative timings.

## 2. Validation & documentation

- [x] 2.1 Verify that the new probes succeed once `/health/ready` is reachable (local `kubectl port-forward` or `kubectl exec` check) and the pod stays in Ready state.
- [x] 2.2 Update `README.md` to mention that health checks are enabled via `KC_HEALTH_ENABLED=true` and note the expected probe paths/ports.
