## Why

ArgoCD must fetch manifests from private GitHub repositories, but the current bootstrap lacks documented credentials management for those repos. Without a secure secret and credential definition, deployments fail every time the GitHub token expires.

## What Changes

- Define where to keep GitHub deploy keys or personal access tokens so ArgoCD can authenticate to private repositories (Kubernetes secret name, namespace, and expected data keys).
- Update existing `infra/services/observability/argocd` manifests (Application or Repository secrets) to consume that secret and document the steps to rotate tokens.
- Add README guidance describing how to create the secret, what environment variables to set in the bootstrap script, and how to scope the GitHub token for minimal permissions.

## Capabilities

### New Capabilities
- `argocd-private-repo-auth`: Securely store GitHub credentials and point ArgoCD’s `repositories` secret to them so private repo syncs are possible.

### Modified Capabilities
- `- None.`

## Impact

- `infra/services/observability/argocd` (adjust Repository/Secret manifest to reference new credentials)
- `scripts/run-all.sh` or bootstrap docs (document how to create/store GitHub token secrets)
- `README.md` (describe the new secret, token scope, and rotation guidance)

## Non-goals

- Building a CI pipeline to rotate tokens automatically in this change.
