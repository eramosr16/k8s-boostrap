## Context

Currently, the Kubernetes cluster does not have authentication configured for pulling container images from AWS ECR. Application workloads requiring private ECR images will fail during image pull.

The solution must:
- Store AWS credentials (access key, secret key, account ID, region) in a Kubernetes Secret
- Configure the secret as an ImagePullSecret on the appropriate ServiceAccount(s)
- Support automatic credential rotation via kubelet credential provider plugin

## Goals / Non-goals

**Goals:**
- Create a Kubernetes Secret containing initial AWS ECR credentials
- Configure ImagePullSecret for the default ServiceAccount to enable pulling from private ECR
- Deploy ECR credential provider daemonset for automatic token refresh
- Document required configuration in `.env-example`
- Provide deployment instructions in the registry folder README

**Non-Goals:**
- Configure ECR repository lifecycle policies
- Set up ECR replication across regions

## Decisions

1. **Secret Type**: Using `kubernetes.io/dockerconfigjson` format for the secret
   - Alternative: Use `aws.amazonaws.com` plugin with ECR IAM roles
   - Selected: dockerconfigjson with credential provider for automatic rotation

2. **Credential Rotation**: Using ECR credential provider daemonset
   - Alternative: IRSA (IAM Roles for Service Accounts)
   - Selected: credential provider daemonset - works without IAM role setup
   - Reference: https://github.com/yuyinws/ecr-credential-provider

3. **Target ServiceAccount**: default namespace default SA
   - Alternative: Create dedicated SA for app workloads
   - Selected: Update default SA for now; can be extended later

4. **Configuration**: Using env file for registry URL, key, secret
   - Location: `infra/services/registry/registry-config.env`
   - Contains: AWS_ACCOUNT_ID, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

## Risks / Trade-offs

- [Risk] Hardcoded credentials in manifest → [Mitigation] Use env file reference, require users to provide values at deploy time
- [Risk] Daemonset fails → [Mitigation] Fallback to static secret; credential provider updates the secret periodically

## Migration Plan

### ArgoCD-managed (Automatic)
1. `aws-ecr-secret.yaml` - Initial credentials secret (updated by credential provider)
2. `registry-config.yaml` - ServiceAccount with ImagePullSecret reference
3. `ecr-credential-provider.yaml` - Daemonset for automatic credential rotation

### Manual Steps (One-time)
1. Create `registry-config.env` with AWS credentials (AWS_ACCOUNT_ID, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
2. Generate initial dockerconfigjson and update secret manifest
3. Deploy credential provider daemonset
4. Commit all manifests to repo for ArgoCD to sync

### Credential Rotation (Automatic)
The ECR credential provider daemonset automatically:
1. Queries AWS ECR for auth tokens (valid for 12 hours)
2. Updates the `ecr-registry` secret with new credentials
3. Runs on each node via daemonset
- No manual intervention needed after initial setup