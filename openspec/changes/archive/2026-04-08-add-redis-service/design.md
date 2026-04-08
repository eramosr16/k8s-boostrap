## Context

The K8s cluster needs a Redis cache service to support applications requiring caching, session storage, or message brokering. Redis will be deployed in the `infra/services/databases/redis/` directory following the existing service structure in the repository.

## Goals / Non-Goals

**Goals:**
- Deploy Redis to the cluster with ArgoCD management
- Configure optional persistence for cache durability
- Ensure Redis is only accessible internally (ClusterIP service)
- Follow repository conventions for service manifests

**Non-Goals:**
- External access to Redis (not exposed via Ingress)
- Redis Cluster or Sentinel for high availability (single instance)
- Authentication requiring complex user management

## Decisions

- **Redis Version**: Use Redis 7 for modern features
- **Storage**: Use Kubernetes PersistentVolumeClaim with standard storage class (optional persistence via RDB)
- **Service Type**: ClusterIP (internal only) - port 6379 not exposed externally
- **Deployment Method**: Kubernetes Deployment with single replica
- **Image**: Use bitnami/redis for production-ready image with sensible defaults
- **ArgoCD Integration**: Create Application manifest in `infra/services/databases/redis/`

## Risks / Trade-offs

- **Risk**: Data loss on pod failure → **Mitigation**: PersistentVolumeClaim ensures data persists
- **Risk**: No backup strategy → **Mitigation**: Out of scope, can be added later
- **Risk**: Single point of failure → **Mitigation**: Acceptable for development; production would need HA setup
