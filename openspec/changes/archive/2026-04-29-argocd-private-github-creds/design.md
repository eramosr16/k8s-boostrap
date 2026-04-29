## Context

- ArgoCD is currently pointed at public repositories only, so any future private GitHub manifests cannot be synchronized; administrators must manually store tokens and edit argocd repositories each time permissions change.
- GitHub deploy keys or PATs need to live in Kubernetes secrets so ArgoCD applications can reference them without exposing credentials in plain text.

## Goals / Non-Goals

**Goals:**

- Define a well-known Kubernetes secret (`argocd-private-github`) containing the token, and keep a README note explaining how to create it with `kubectl` or `scripts/run-all.sh`.
- Update the ArgoCD repository or Application manifest to reference that secret (either via repository credentials or repo entry under `argocd-repo-server` configuration).

**Non-Goals:**

- Automated rotation of the GitHub token.
- Supporting OAuth or other identity providers beyond the basic token/SSH key method.

## Decisions

- Store the credential data in `kubernetes.io/basic-auth` or `ssh-auth` secret format depending on whether a PAT or deploy key is used; default to PAT with `username=git` or `github`.
- Document token scope as read-only (`repo` minimal) so operators know how to request tokens from GitHub while limiting damage.
- Use existing bootstrap scripts/documentation to instruct operators to create the secret before running ArgoCD, keeping the script simple but the README explicit.

## Risks / Trade-offs

- [Secret leakage] Tokens stored in Kubernetes secrets must still be rotated; mitigate via README instructions and `kubectl` commands to update the secret.
- [Permission granularity] Using a PAT requires `repo` scope; limit to read-only if possible to reduce exposure.
