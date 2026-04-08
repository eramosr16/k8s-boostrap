## Context

This project provides bootstrap scripts to set up a local Kubernetes development environment. K3s is a lightweight Kubernetes distribution ideal for local development. ArgoCD will be installed to enable GitOps-based deployments from this repository.

## Goals / Non-Goals

**Goals:**
- Provide idempotent scripts that can be run multiple times safely
- Use official K3s and ArgoCD installation methods
- Include proper error handling and user feedback
- Configure kubectl context automatically after K3s installation

**Non-Goals:**
- Production-grade hardening or multi-node setup
- Automated SSL/TLS certificate management
- Integration with external authentication providers
- Backup/restore functionality

## Decisions

1. **K3s Installation Method**: Use the official K3s install script (`curl -sfL https://get.k3s.io | sh -`) - this is the recommended approach from k3s.io

2. **ArgoCD Installation**: Use standard Kubernetes manifests from ArgoCD documentation (non-HA mode for local development)

3. **Script Location**: Place scripts in `scripts/` directory at repo root for easy access

4. **Idempotency**: Each script checks if its prerequisites are already installed before proceeding

## Risks / Trade-offs

- **Risk**: Script requires root/sudo access to install K3s
  - **Mitigation**: Document sudo requirement in script output

- **Risk**: Existing K3s installation might be overwritten
  - **Mitigation**: Script checks for existing installation and warns user

- **Risk**: ArgoCD UI might not be accessible due to port conflicts
  - **Mitigation**: Use default port 8080 and document how to change if needed