## Why

A bootstrap script is needed to automate the setup of a local Kubernetes cluster using K3s and install ArgoCD for GitOps-based deployments. This provides a reproducible, one-command way to spin up a complete development environment.

## What Changes

- Create a bash script (`scripts/bootstrap.sh`) that installs K3s
- Create a bash script (`scripts/install-argocd.sh`) that installs ArgoCD via kubectl
- Both scripts should be idempotent and include proper error handling

## Capabilities

### New Capabilities
- `k3s-bootstrap`: Bash script to install and configure K3s single-node cluster
- `argocd-installation`: Bash script to deploy ArgoCD to the K3s cluster

### Modified Capabilities
- None

## Impact

- New scripts directory with bootstrap scripts
- Users can spin up a local cluster with ArgoCD by running two commands

## Non-Goals

- Multi-node K3s cluster setup
- Integration with cloud providers
- SSL/TLS configuration for ArgoCD (use default for now)