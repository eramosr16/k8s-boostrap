## Context

The K8s cluster needs a PostgreSQL database service to support applications requiring relational data storage. PostgreSQL will be deployed in the `infra/services/databases/postgres/` directory following the existing service structure in the repository.

## Goals / Non-Goals

**Goals:**
- Deploy PostgreSQL to the cluster with ArgoCD management
- Configure persistent storage for data durability
- Ensure PostgreSQL is only accessible internally (ClusterIP service)
- Follow repository conventions for service manifests

**Non-Goals:**
- External access to PostgreSQL (not exposed via Ingress)
- High availability or replication (single instance)
- Database user management at application level

## Decisions

- **PostgreSQL Version**: Use PostgreSQL 16 for modern features and security
- **Storage**: Use Kubernetes PersistentVolumeClaim with standard storage class
- **Service Type**: ClusterIP (internal only) - port 5432 not exposed externally
- **Deployment Method**: Kubernetes Deployment with single replica
- **Image**: Use bitnami/postgresql for production-ready image with sensible defaults
- **ArgoCD Integration**: Create Application manifest in `infra/services/databases/postgres/postgres.yaml`

## Risks / Trade-offs

- **Risk**: Data loss on pod failure → **Mitigation**: PersistentVolumeClaim ensures data persists
- **Risk**: No backup strategy → **Mitigation**: Out of scope, can be added later
- **Risk**: Single point of failure → **Mitigation**: Acceptable for development; production would need HA setup
