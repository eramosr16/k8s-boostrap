## 1. Update ArgoCD Root App

- [x] 1.1 Update bootstrap/root-app.yaml to watch `infra/` directory instead of `apps/`
- [x] 1.2 Set targetRevision to main branch
- [x] 1.3 Ensure recurse: true is set for directory scanning

## 2. Verify Deployment

- [x] 2.1 Validate YAML syntax with kubectl dry-run (used Python yaml.safe_load - valid)
- [ ] 2.2 Test ArgoCD sync status after deployment (requires running cluster)