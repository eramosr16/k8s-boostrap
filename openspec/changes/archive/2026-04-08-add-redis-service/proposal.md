## Why

The K8s cluster needs a Redis cache service to support applications requiring caching, session storage, or message brokering. Currently, there is no Redis service deployed, which limits application performance and data handling capabilities.

## What Changes

- Deploy Redis to the `infra/services/databases/redis/` directory
- Create ArgoCD Application manifest for Redis deployment
- Configure Redis with internal-only network access (port 6379 not exposed externally)
- Add necessary Kubernetes resources (Deployment, Service, ConfigMap, PersistentVolumeClaim)

## Capabilities

### New Capabilities
- `redis-cache`: Redis cache service with optional persistence

### Modified Capabilities
- None

## Impact

- New directory: `infra/services/databases/redis/`
- ArgoCD will manage Redis deployment through the App-of-Apps pattern
- Internal services can connect to Redis via `redis.infra.svc.cluster.local:6379`
