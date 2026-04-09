## Context

Currently, setting up the cluster requires:
1. Running `bootstrap.sh` to install K3s
2. Running `install-argocd.sh` to install ArgoCD
3. Manually creating secrets in Kubernetes (since they're not in git for security)
4. Manually applying ArgoCD Applications or waiting for them to sync

This is error-prone and requires understanding of the system.

## Goals / Non-Goals

**Goals:**
- Single `run-all.sh` script that orchestrates end-to-end cluster setup
- Interactive credential prompts with validation
- Direct Kubernetes secret creation via kubectl
- Health check polling for all services
- Clear exit status and messages

**Non-Goals:**
- Implementing sealed secrets or external secrets operator
- Modifying existing service deployment configurations
- Supporting non-interactive (CI) mode (future enhancement)

## Decisions

1. **Script location**: `scripts/run-all.sh` (alongside existing scripts)

2. **Credential flow**: 
   - Prompt for each secret interactively using `read -s` (silent input)
   - Validate non-empty input
   - Create secrets directly via `kubectl create secret`
   - This bypasses the need for envsubst or git-stored secrets

3. **Secret handling approach**:
   - Parse existing secret YAML files to determine what keys are needed
   - Create secrets in `infra` namespace directly
   - Skip git-stored secrets entirely for initial bootstrap

4. **Health check approach**:
   - Wait for ArgoCD root Application to be Synced
   - Poll each service Application for Healthy status
   - Use `kubectl get applications -n argocd` to check status
   - Timeout after 5 minutes with clear error message

5. **ArgoCD repo URL**:
   - Detect if running locally (file://) or use current git remote
   - Prompt user to confirm or override

## Risks / Trade-offs

- **[Risk] Secrets in shell history**: Using `read -s` prevents visible passwords
  - **Mitigation**: Use `unset` to clear variables after use, advise user to use `.env` file
- **[Risk] Long polling time**: Services may take time to download images
  - **Mitigation**: Configurable timeout with progress indicators
- **[Risk] Git not initialized**: If repo isn't set up, ArgoCD can't pull
  - **Mitigation**: Check git remote exists, prompt for repoURL if needed

## Migration Plan

1. Create `scripts/run-all.sh` 
2. Test on fresh K3s installation
3. Document usage in README.md
