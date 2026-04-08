## 1. Create Keycloak Manifest Directory

- [x] 1.1 Create directory `infra/services/iam/keycloak/`

## 2. Create Keycloak Kubernetes Resources

- [x] 2.1 Create Keycloak Deployment manifest
- [x] 2.2 Create Keycloak Service (ClusterIP)
- [x] 2.3 Create ConfigMap for Keycloak configuration
- [x] 2.4 Create Secret for Keycloak passwords
- [x] 2.5 Create IngressRoute for external access via Traefik

## 3. Create ArgoCD Application Manifest

- [x] 3.1 Create ArgoCD Application in `infra/services/iam/keycloak/`

## 4. Update Documentation

- [x] 4.1 Add Keycloak to README.md service details
- [x] 4.2 Add Keycloak secrets to Managing Secrets section
- [x] 4.3 Add auth.mydomain.com to pre-deployment checklist

## 5. Validate and Test

- [x] 5.1 Validate YAML syntax with kubectl dry-run
- [x] 5.2 Verify manifests follow repository conventions
