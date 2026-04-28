## ADDED Requirements

### Requirement: Keycloak deployment uses Bitnami image and env schema
The Keycloak deployment under `infra/services/iam/keycloak` SHALL use `docker.io/bitnami/keycloak:latest` as its container image, expose container port 8080, and set the environment variables `KEYCLOAK_DATABASE_HOST`, `KEYCLOAK_DATABASE_NAME`, and `KEYCLOAK_DATABASE_USER` so the Bitnami wrapper can configure its JDBC connection automatically.

#### Scenario: Bitnami env vars connect to postgres
- **WHEN** ArgoCD applies the updated deployment manifest
- **THEN** the resulting pod starts a container using `docker.io/bitnami/keycloak:latest` with `KEYCLOAK_DATABASE_HOST=postgresql`, `KEYCLOAK_DATABASE_NAME=bitnami_keycloak`, and `KEYCLOAK_DATABASE_USER=bn_keycloak` and the container becomes ready within readinessProbe thresholds.

### Requirement: Existing secrets provide credentials
The deployment SHALL continue to source `KEYCLOAK_ADMIN_PASSWORD` and `KEYCLOAK_DATABASE_PASSWORD` from the existing `keycloak-secret` so no new plaintext credentials are introduced.

#### Scenario: Secret-backed credentials persist
- **WHEN** the Bitnami-enabled pod is created
- **THEN** it mounts `keycloak-secret` and the container logs show that it read the admin and database passwords without requiring a manual update to the ArgoCD application.
