## 1. Remove Portainer

- [x] 1.1 Delete the `infra/services/observability/portainer/` directory
- [x] 1.2 Remove Portainer references from README.md

## 2. Create Headlamp Resources

- [x] 2.1 Create `infra/services/observability/headlamp/` directory
- [x] 2.2 Create headlamp-deployment.yaml
- [x] 2.3 Create headlamp-service.yaml
- [x] 2.4 Create headlamp-pvc.yaml (not needed, skip)
- [x] 2.5 Create headlamp-secret.yaml (not needed for basic auth)
- [x] 2.6 Create headlamp-app.yaml for ArgoCD
- [x] 2.7 Create headlamp-ingressroute.yaml for Traefik

## 3. Configure RBAC

- [x] 3.1 Create headlamp-serviceaccount.yaml
- [x] 3.2 Create headlamp-clusterrole.yaml with read-only or admin permissions
- [x] 3.3 Create headlamp-clusterrolebinding.yaml

## 4. Update Documentation

- [x] 4.1 Update README.md with Headlamp service details
- [x] 4.2 Update DNS checklist for headlamp.mydomain.com