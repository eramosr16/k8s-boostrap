## Why

Running kube-score against all Kubernetes manifests revealed multiple security and reliability issues across all 10+ services. These include missing security contexts, missing image pull policies, missing resource limits, and a broken StatefulSet configuration for Loki. Addressing these improves cluster security and prevents potential runtime issues.

## What Changes

- Fix Loki StatefulSet missing `serviceName` reference
- Add security context to all deployments/daemonsets (runAsNonRoot, runAsUser, fsGroup)
- Add `imagePullPolicy: Always` to all container specs
- Add ephemeral storage limits to all containers
- Fix duplicate liveness/readiness probes (headlamp, keycloak, opentelemetry)
- Add NetworkPolicy manifests (optional for single-node, but good practice)

## Capabilities

### New Capabilities
- `security-contexts`: Add security contexts to all workloads
- `image-pull-policy`: Ensure all images use Always pull policy
- `resource-limits`: Add ephemeral storage and proper resource limits

### Modified Capabilities
- `loki-stack`: Fix StatefulSet serviceName reference
- `promtail-agent`: Add security context and image pull policy

## Impact

All service deployments in `infra/services/` will be updated with proper security contexts and resource limits.

## Non-Goals

- Add NetworkPolicies (optional for single-node K3s)
- Change container image versions
- Modify resource CPU/memory requests (already set)