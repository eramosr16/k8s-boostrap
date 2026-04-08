## Context

The K8s cluster needs an Identity and Access Management (IAM) solution to handle authentication and authorization for all applications. Keycloak will be deployed as the central identity provider, connecting to PostgreSQL for persistence and exposed via Traefik for external access.

## Goals / Non-Goals

**Goals:**
- Deploy Keycloak to the cluster with ArgoCD management
- Connect Keycloak to existing PostgreSQL database
- Expose Keycloak externally via Traefik at `auth.mydomain.com`
- Follow repository conventions for service manifests
- Use environment variable placeholders for secrets

**Non-Goals:**
- High availability or clustering (single instance for now)
- Custom Keycloak themes or extensions
- Integration with external LDAP/AD directories

## Decisions

- **Keycloak Version**: Use Keycloak 24 (latest stable)
- **Database**: Use existing PostgreSQL service (`postgres.infra.svc.cluster.local:5432`)
- **Service Type**: ClusterIP for internal access, IngressRoute for external
- **Deployment Method**: Kubernetes Deployment with single replica
- **Image**: Use bitnami/keycloak for production-ready image
- **Ingress**: Create IngressRoute for Traefik at `auth.mydomain.com`
- **Secrets**: Use environment variable placeholders (`${KEYCLOAK_ADMIN_PASSWORD}`, `${KEYCLOAK_DATABASE_PASSWORD}`)
- **ArgoCD Integration**: Create Application manifest in `infra/services/iam/keycloak/`

## Risks / Trade-offs

- **Risk**: Single point of failure → **Mitigation**: Acceptable for development; production would need HA setup
- **Risk**: Database connection issues → **Mitigation**: Ensure PostgreSQL is deployed before Keycloak
- **Risk**: TLS certificate not ready → **Mitigation**: Use HTTP initially, cert-manager will provision Let's Encrypt
