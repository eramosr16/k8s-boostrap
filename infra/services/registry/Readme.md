# AWS ECR Registry Configuration

This folder contains Kubernetes manifests to configure registry authentication for pulling container images from AWS ECR.

## Files

| File | ArgoCD-managed | Description |
|------|----------------|-------------|
| `aws-ecr-secret.yaml` | ✅ Yes | Initial K8s Secret with ECR credentials |
| `registry-config.yaml` | ✅ Yes | ServiceAccount with ImagePullSecret reference |
| `ecr-credential-provider.yaml` | ✅ Yes | DaemonSet for automatic credential rotation |
| `registry-config.env` | ❌ No | AWS credentials (add to .gitignore) |

## Prerequisites

1. AWS account with ECR repository access
2. AWS credentials with permission to pull images from ECR

## Configuration

### 1. Create registry-config.env

```bash
cp registry-config.env.template registry-config.env
# Edit with your actual AWS credentials
```

### 2. Update AWS Credentials

Edit `registry-config.env` with your AWS details:
- `AWS_ACCOUNT_ID`: Your AWS account ID (e.g., 123456789012)
- `AWS_REGION`: ECR repository region (e.g., us-east-1)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key

## Deployment

### ArgoCD-managed (Automatic)

```bash
git add .
git commit -m "Add AWS ECR registry auth"
git push
```

ArgoCD will automatically sync all manifests.

## Automatic Credential Rotation

The ECR credential provider DaemonSet automatically:
1. Runs on each node as a DaemonSet
2. Queries AWS ECR for auth tokens (valid for 12 hours)
3. Updates the `ecr-registry` secret with new credentials
4. Refreshes tokens every 6 hours (configurable via REFRESH_INTERVAL)

### How it works

- The credential provider container runs with host network access
- It has RBAC permissions to update the `ecr-registry` secret in the `default` namespace
- When a pod tries to pull an image, kubelet reads the refreshed credentials from the secret

## Manual Rotation (Fallback)

If the credential provider fails:

1. Regenerate ECR token:
   ```bash
   aws ecr get-login-password --region us-east-1
   ```

2. Re-encode as base64 and update `aws-ecr-secret.yaml`

3. Commit and push - ArgoCD will sync

## Troubleshooting

- **ImagePullBackOff**: Check if secret exists and credentials are valid
- **Credential provider not running**: Check DaemonSet status
- **Token expired**: Verify credential provider is updating the secret

## Security Notes

- Add `registry-config.env` to `.gitignore` to avoid committing secrets
- Consider using IRSA for production clusters (automatic IAM-based rotation)