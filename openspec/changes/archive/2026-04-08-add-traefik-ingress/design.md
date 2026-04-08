## Context

K3s bundles Traefik 2.x as the default ingress controller. It provides basic routing capabilities but lacks TLS certificate management. This design outlines how to configure Traefik with Let's Encrypt for automatic certificate provisioning.

## Goals / Non-Goals

**Goals:**
- Configure Traefik with Let's Encrypt cert-manager integration for automatic TLS
- Enable HTTP to HTTPS redirect
- Add security middleware (headers, rate limiting)
- Provide secure access to Traefik dashboard

**Non-Goals:**
- Custom Traefik installation (use K3s bundled version)
- Advanced middleware configurations beyond basics
- External DNS integration (separate service)

## Decisions

### TLS Certificate Strategy
**Decision:** Use Let's Encrypt with HTTP-01 challenge via Traefik's ACME provider.

**Rationale:** HTTP-01 is the simplest method - requires no external DNS configuration. Works well for clusters accessible from the internet or with port-forwarded access.

**Alternative Considered:** DNS-01 challenge - more complex, requires provider credentials, but works for internal networks. Not needed for initial setup.

### Traefik Configuration Approach
**Decision:** Use Kubernetes CRDs (IngressRoute, Middleware, TLSOption) for configuration.

**Rationale:** Native Kubernetes way, declarative, works well with ArgoCD. K3s has Traefik CRDs pre-installed.

### Dashboard Access
**Decision:** Enable dashboard with basic auth via Kubernetes Secret, exposed through Ingress.

**Rationale:** Allows debugging and monitoring. Secured with basic auth to prevent unauthorized access.

## Risks / Trade-offs

- [Risk] Let's Encrypt rate limits → Mitigation: Use staging server for testing, or configure cert-manager for production
- [Risk] HTTP-01 challenge requires port 80 accessible → Mitigation: Ensure firewall allows incoming HTTP/HTTPS
- [Risk] Traefik dashboard exposed → Mitigation: Basic auth required, consider limiting to internal networks

## Migration Plan

1. Apply Traefik configuration manifests via kubectl or ArgoCD
2. Verify Traefik picks up new configuration
3. Test certificate issuance with a sample Ingress(Manual testing would be done, not actual test besides the validation of the script)
4. Update documentation with usage examples