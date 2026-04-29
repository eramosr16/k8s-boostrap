## 1. Credential setup

- [x] 1.1 Document and/or script the `kubectl create secret generic argocd-private-github --from-literal=username=git --from-literal=password=<token>` command so operators can store GitHub AT indicators.
- [x] 1.2 Update the ArgoCD repository manifest (or secret consumed by the repo server) to use `argocd-private-github` for SSH/PAT authentication when syncing private repos.

## 2. Validation & documentation

- [x] 2.1 Validate that ArgoCD can reach a private GitHub repo by running `argocd repo add <url> --username git --password <token>` (dry-run or actual to confirm success) and log steps.
- [x] 2.2 Update `README.md` covering the new secret, token scope, and instructions to rotate the credentials with `kubectl`.
