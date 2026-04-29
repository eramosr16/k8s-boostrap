## ADDED Requirements

### Requirement: Store GitHub credentials for ArgoCD
ArgoCD SHALL read GitHub deploy credentials from a well-known Kubernetes secret (e.g., `argocd-private-github`) containing the token or SSH key so private repositories can be accessed without embedding secrets in manifests.

#### Scenario: Private repo sync uses secret
- **WHEN** ArgoCD pulls a repo defined as private
- **THEN** it references the `argocd-private-github` secret for authentication and successfully clones without prompting for credentials.

### Requirement: Documentation for token creation
The README SHALL describe how operators create or rotate the GitHub token or deploy key and how to scope its permissions (minimum `repo` read access) before applying ArgoCD manifests.

#### Scenario: Operator rotates credentials
- **WHEN** an operator rotates the GitHub token
- **THEN** they update the `argocd-private-github` secret via `kubectl create secret generic ... --from-literal=token=<new>` and ArgoCD continues syncing the private repository.
