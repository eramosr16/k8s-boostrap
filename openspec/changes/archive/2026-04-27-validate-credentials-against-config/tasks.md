## 1. Prompt & export alignment

- [x] 1.1 Extend `prompt_secrets()` to iterate over a single definition list that covers every credential/secret (env var, description, allow-empty flag).
- [x] 1.2 Remove any credential harvesting from `config.yaml`, ensuring `prompt_secrets()` remains the only way secrets are collected.

## 2. Documentation & validation

- [x] 2.1 Align the exported environment variables with the new prompt list and ensure each exported secret is actually requested by `prompt_secrets()`.
- [x] 2.2 Document in `README.md` that credential secrets are collected interactively by `scripts/run-all.sh` and should not live in `config.yaml`.
