## Context

Currently the platform runs services (PostgreSQL, Redis, RabbitMQ, Keycloak, Grafana, Loki, Prometheus) via ArgoCD in the `infra` namespace. We need to add Nuclio as a serverless functions platform. Nuclio requires:
- A dedicated namespace (`nuclio`)
- CRDs for function definitions
- Controller deployment
- Dashboard for UI management
- Traefik ingress for dashboard access
- Keycloak integration for authentication

## Goals / Non-Goals

**Goals:**
- Deploy Nuclio controller and dashboard to Kubernetes via Helm
- Configure ECR as the function image registry
- Use Kaniko as secure container builder (no Docker socket binding)
- Expose dashboard via Traefik with HTTPS
- Integrate dashboard with Keycloak OAuth2
- Make Nuclio service deployable via ArgoCD

**Non-Goals:**
- Pre-configured function examples (separate task)
- Multi-cluster Nuclio setup
- Air-gapped deployment (future enhancement)

## Decisions

1. **Nuclio Version**: Freeze a specific qualified version for production
   - Alternative: Use latest stable
   - Decision: Pin specific version in Helm values, upgrade after testing
   - Rationale: Production requires reproducibility

2. **Installation Method**: Helm charts (preferred for production)
   - Alternative: Direct kubectl apply with YAML manifests
   - Decision: Use official Nuclio Helm chart from https://nuclio.github.io/nuclio/charts
   - Rationale: Better maintenance, easier upgrades, production-oriented features

3. **Container Builder**: Kaniko (security best practice)
   - Alternative: Bind-mount Docker socket (security risk)
   - Decision: Use Kaniko for building function images
   - Rationale: No root access to host, works with Kubernetes RBAC

4. **Registry**: Amazon ECR for function images
   - Alternative: Docker Hub, GCR, ACR
   - Decision: Use ECR (configured in config.yaml)
   - Rationale: Private registry with IAM integration, pull-through caching

5. **Authentication**: Traefik OAuth2 forwardauth with Keycloak
   - Decision: Reuse existing `infra-keycloak` middleware pattern
   - Enables SSO without embedding credentials in Nuclio

6. **Ingress**: Traefik CRDs (IngressRoute) + OAuth2 middleware
   - Decision: Create IngressRoute for dashboard, Middleware for OAuth2

7. **Metrics**: Prometheus for function and system metrics
   - Decision: Use Prometheus pull for system, push for functions
   - Rationale: Standard Prometheus integration, existing Prometheus in infra namespace

8. **Broker**: RabbitMQ as default message broker
   - Decision: Use existing RabbitMQ service from infra namespace
   - Rationale: Reuse existing broker, avoid deploying separate service
   - URL: rabbitmq://rabbitmq.infra.svc.cluster.local:5672

9. **Platform Configuration**: ConfigMap for platform-wide settings
   - Decision: Create platform-config ConfigMap in nuclio namespace
   - Rationale: Centralized configuration for all functions

## Risks / Trade-offs

- [Risk] ECR token expires every 12 hours → [Mitigation] Set up cron job to refresh token
- [Risk] Kaniko requires registry credentials → [Mitigation] Create ECR secret and AWS credentials secret
- [Risk] Dashboard timeout with OAuth2 → [Mitigation] Configure adequate timeouts in middleware
- [Risk] Nuclio CRD conflicts with existing serverless frameworks → [Mitigation] Use dedicated namespace
- [Risk] Prometheus metrics not scraped → [Mitigation] Create ServiceMonitor for Prometheus operator

## Migration Plan

1. Add Nuclio Helm repo
2. Configure ECR credentials and secrets
3. Create Helm values file with Kaniko configuration
4. Install Nuclio via Helm: `helm install nuclio nuclio/nuclio`
5. Create platform-config ConfigMap with Prometheus and RabbitMQ settings
6. Create ServiceMonitor for Prometheus metrics
7. Apply Traefik ingress with OAuth2 middleware
8. Verify pods running: `kubectl -n nuclio get pods`
9. Access dashboard at `https://nuclio.${CLUSTER_DOMAIN}`

## Open Questions

- Which ECR region to use (match cluster region)
- ECR token refresh schedule