## 1. Manifest updates

- [x] 1.1 Replace the Keycloak Deployment container definition with `docker.io/bitnami/keycloak:latest` and configure `KEYCLOAK_DATABASE_HOST/NAME/USER` per the spec while keeping the current secrets for passwords.
- [x] 1.2 Confirm the Keycloak Service manifest still exposes port 8080, and adjust annotations only if the new image requires it.

## 2. Validation & documentation

- [x] 2.1 Run `kubectl apply --dry-run=client -f infra/services/iam/keycloak/keycloak-deployment.yaml` (and service manifest if touched) to validate the syntax before pushing the change.
- [x] 2.2 Add a brief entry to `README.md` describing the Keycloak Bitnami upgrade so future readers know why the manifest changed.
