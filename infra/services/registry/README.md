# AWS ECR Registry Configuration

This folder contains Kubernetes manifests to configure registry authentication for pulling container images from AWS ECR.

## Files

| File | ArgoCD-managed | Description |
|------|----------------|-------------|
| `aws-ecr-secret.yaml` | ✅ Yes | Initial K8s Secret with ECR credentials |
| `registry-config.yaml` | ✅ Yes | ServiceAccount with ImagePullSecret reference |
| `ecr-credential-provider.yaml` | ✅ Yes | CronJob `refresh-ecr-registry-secret` (plus RBAC/ServiceAccount) that refreshes the `ecr-registry` pull secret every 10 minutes |
| `registry-config.env.example` | ❌ No | Template for AWS credentials (copy to `registry-config.env` before you create the `ecr-refresh-aws-creds` secret) |

## Prerequisites

1. AWS account with ECR repository access
2. AWS credentials with permission to pull images from ECR

## Configuration

### 1. Create registry-config.env

```bash
cp registry-config.env.example registry-config.env
# Edit with your actual AWS credentials
```

### 2. Update AWS Credentials

Edit `registry-config.env` with your AWS details:
- `AWS_ACCOUNT_ID`: Your AWS account ID (e.g., 123456789012)
- `AWS_REGION`: ECR repository region (e.g., us-east-1)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key

### 3. Create the refresh secret

Once the env file has the correct values, create the credentials secret that the CronJob consumes (skip this if `scripts/run-all.sh` already created `ecr-refresh-aws-creds` because you provided the AWS credentials there):

```bash
kubectl create secret generic ecr-refresh-aws-creds \
  --namespace infra \
  --from-env-file=infra/services/registry/registry-config.env \
  --dry-run=client -o yaml | kubectl apply -f -
```

## Deployment

### ArgoCD-managed (Automatic)

```bash
git add .
git commit -m "Add AWS ECR registry auth"
git push
```

ArgoCD will automatically sync all manifests.

## Automatic Credential Rotation

The `refresh-ecr-registry-secret` CronJob runs every 10 minutes in the `infra` namespace, downloads `kubectl`, and uses the AWS CLI to rotate the `ecr-registry` pull secret in the `default` namespace by calling `aws ecr get-login-password`. The job relies on the `ecr-refresh-aws-creds` secret for AWS credentials and uses a ClusterRole/ServiceAccount to patch the secret.

### How it works

- The CronJob runs the public `public.ecr.aws/aws-cli/aws-cli:2.27.41` image with the AWS credentials injected via `envFrom`.
- It writes the refreshed docker-registry secret for `${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com` into the `default` namespace so node kubelets can pull private images.
- The `registry-config.yaml` service account (stored in `kube-system`) lists `ecr-registry` in `imagePullSecrets` so every pod can benefit from the rotated credentials.

## Manual Rotation (Fallback)

If the credential rotation CronJob fails:

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
