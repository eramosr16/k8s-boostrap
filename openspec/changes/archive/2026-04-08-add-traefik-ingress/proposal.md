## Why

K3s comes with Traefik as the default ingress controller, but it's not configured with TLS certificate management. We need to configure Traefik with Let's Encrypt for automatic TLS certificate provisioning to secure incoming HTTP traffic to services deployed in the cluster.

## What Changes

- Add Traefik Configuration manifest with Let's Encrypt cert resolver
- Configure HTTP to HTTPS redirect
- Set up middleware for security headers
- Add middleware for basic auth on dashboard (traefik dashboard would not be exposed to the public), but include the middleware in case we need it on the future

## Capabilities

### New Capabilities
- `traefik-ingress`: Configure Traefik as ingress controller with Let's Encrypt TLS management
- `traefik-dashboard`: Enable Traefik dashboard but don't add a public ingress to it, keep it accessible internally only

### Modified Capabilities
- None

## Impact

- New YAML manifests in `infra/services/gateway/` directory
- ArgoCD will deploy these as part of the services layer

## Non-goals

- Custom Traefik deployment (using K3s bundled version)
- Advanced middleware configurations beyond basics
- Integration with external DNS (handled separately)