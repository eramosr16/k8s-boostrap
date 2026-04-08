## Why

The K8s cluster needs a persistent PostgreSQL database service to support applications requiring relational data storage. Currently, there is no database service deployed, which limits the types of applications that can be run on the cluster.

## What Changes

- Deploy PostgreSQL to the `infra/services/databases/postgres/` directory
- Create ArgoCD Application manifest for Postgres deployment
- Configure PostgreSQL with internal-only network access (port 5432 not exposed externally)
- Add necessary Kubernetes resources (Deployment, Service, ConfigMap, PersistentVolumeClaim)

## Capabilities

### New Capabilities
- `postgres-database`: PostgreSQL database service with persistent storage

### Modified Capabilities
- None

## Impact

- New directory: `infra/services/databases/postgres/`
- ArgoCD will manage PostgreSQL deployment through the App-of-Apps pattern
- Internal services can connect to PostgreSQL via `postgres.internal.svc.cluster.local:5432`
