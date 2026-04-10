## 1. Update Headlamp Deployment

- [x] 1.1 Add OIDC environment variables to headlamp-deployment.yaml
- [x] 1.2 Add OIDC secret volume mount to headlamp-deployment.yaml

## 2. Create OIDC Secret

- [x] 2.1 Create headlamp-oidc-secret.yaml with OIDC credentials

## 3. Update RBAC

- [x] 3.1 Update headlamp-clusterrole.yaml to add impersonation permissions

## 4. Update Bootstrap Script

- [x] 4.1 Add Headlamp OIDC client creation to configure_keycloak_clients
- [x] 4.2 Add retrieval of Headlamp client secret
- [x] 4.3 Add creation of headlamp-oidc-secret with credentials