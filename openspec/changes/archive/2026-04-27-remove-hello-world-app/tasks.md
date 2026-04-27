## 1. Manifest Cleanup

- [x] 1.1 Remove the `hello-world` application entry from the ArgoCD root/aggregator manifest so it no longer targets that directory.
- [x] 1.2 Delete `infra/applications/hello-world/` and confirm no other manifests reference that path.

## 2. Documentation & Validation

- [x] 2.1 Update `README.md` to record that the `hello-world` app was intentionally removed.
- [x] 2.2 Run repository checks (git status, kubectl dry-run on preserved manifests) to confirm the tree stays consistent after the removal.
