## Why

Currently, setting up the cluster requires running multiple scripts in sequence (bootstrap.sh, install-argocd.sh), then manually configuring secrets before ArgoCD can deploy services. This creates friction and opportunities for errors during initial cluster setup.

## What Changes

- Create `run-all.sh` script that orchestrates the entire cluster bootstrap process
- Prompt user for all required credentials interactively before deployment
- Create Kubernetes secrets directly with kubectl (since ArgoCD manages deployments, not initial secrets)
- Poll cluster to verify all services reach healthy state
- Exit with clear status message

## Capabilities

### New Capabilities
- **bootstrap-automation**: Automated end-to-end cluster bootstrap with credential handling

## Non-goals

- Modifying existing service configurations
- Changing the ArgoCD installation approach
- Implementing sealed secrets or external secrets manager (secrets created directly via kubectl)
