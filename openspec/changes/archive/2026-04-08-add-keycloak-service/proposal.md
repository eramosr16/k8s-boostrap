## Why

The K8s cluster needs an Identity and Access Management (IAM) solution to handle authentication and authorization for both internal and external applications. Keycloak will provide single sign-on (SSO), user management, and security token services for the entire cluster.

## What Changes

- Deploy Keycloak to the `infra/services/iam/keycloak/` directory
- Create ArgoCD Application manifest for Keycloak deployment
- Configure Keycloak to use PostgreSQL as its database
- Expose Keycloak via Traefik IngressRoute at `auth.mydomain.com`
- Add necessary Kubernetes resources (Deployment, Service, ConfigMap, Secret)

## Capabilities

### New Capabilities
- `keycloak-iam`: Keycloak identity provider with PostgreSQL backend

### Modified Capabilities
- None

## Impact

- New directory: `infra/services/iam/keycloak/`
- ArgoCD will manage Keycloak deployment through the App-of-Apps pattern
- Keycloak accessible externally at `https://auth.mydomain.com`
- Internal services can connect to Keycloak via `keycloak.infra.svc.cluster.local:8080`
