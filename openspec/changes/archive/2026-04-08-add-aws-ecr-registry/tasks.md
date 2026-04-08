## 1. Configuration Files

- [ ] 1.1 Create `infra/services/registry/registry-config.env` with AWS credentials template
- [ ] 1.2 Update `.env-example` to include registry configuration

## 2. Kubernetes Manifests (ArgoCD-managed)

- [ ] 2.1 Create AWS ECR Secret manifest (aws-ecr-secret.yaml) with dockerconfigjson type
- [ ] 2.2 Create ServiceAccount manifest (registry-config.yaml) with ImagePullSecret reference
- [ ] 2.3 Create ECR credential provider DaemonSet (ecr-credential-provider.yaml)

## 3. Initial Deployment (Manual)

- [ ] 3.1 Create registry-config.env with actual AWS credentials
- [ ] 3.2 Generate initial Docker config JSON from AWS credentials
- [ ] 3.3 Update aws-ecr-secret.yaml with base64-encoded config
- [ ] 3.4 Commit manifests to repo for ArgoCD to sync

## 4. Validation

- [ ] 4.1 Verify YAML syntax is valid
- [ ] 4.2 Verify all files exist in correct locations
- [ ] 4.3 Verify credential provider daemonset is running

## 5. Automatic Credential Rotation

- [ ] 5.1 ECR credential provider automatically refreshes tokens every 12 hours
- [ ] 5.2 No manual intervention required after initial setup