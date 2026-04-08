## Why

The cluster needs to authenticate with AWS ECR to pull container images for application workloads. Without proper registry authentication configured in Kubernetes, image pulls from private ECR repositories will fail.

## What Changes

- Add Kubernetes Secret for AWS ECR registry credentials
- Add K8s Manifest to register AWS ECR as a registry pull secret
- Document required environment variables in `.env-example`
- Create README in registry folder with deployment notes

## Capabilities

### New Capabilities
- `aws-ecr-registry-auth`: Configure Kubernetes to authenticate with AWS ECR for pulling container images

### Modified Capabilities
- None

## Non-goals

- Automate AWS credential rotation (handled separately via IRSA or external secrets)
- Configure ECR repository lifecycle policies

## Impact

- New manifest: `infra/services/registry/aws-ecr-secret.yaml`
- New manifest: `infra/services/registry/registry-config.yaml`
- New file: `infra/services/registry/Readme.md`
- Updates to: `.env-example` (add AWS credentials template)