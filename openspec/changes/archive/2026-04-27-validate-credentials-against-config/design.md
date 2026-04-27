## Context

`scripts/run-all.sh` collects secrets via `prompt_secrets()` and exports them before creating Kubernetes secrets. However, the current logic duplicates credential locations: some secrets live in `config.yaml` while the script still prompts for them, which can leak sensitive data if operators accidentally commit the config. At the same time the list of exported variables is longer than the number of prompts, so operators either see misleading prompts or find that the script still errors because a variable was never asked for.

## Goals / Non-Goals

- Ensure the prompt workflow remains the single source of truth for secrets so we never leak them through `config.yaml` while still aligning prompts and exports.
- Keep exported variables aligned with the actual prompts so every secret get collected and usable.
- Document the new behavior so users know why some values are read from config and others must be entered interactively.

- Eliminating interactive secrets entirely (manual input is still required for values that aren’t in the config).
- Moving credential storage to an external secrets manager.

## Decisions

- **Prompt-only secrets:** Keep credential collection inside `prompt_secrets()` so we only gather sensitive values through interactive input, and remove any fallback that silently reads them from `config.yaml`.
- **Prompt/export alignment:** Enumerate the required secrets once and iterate over them for prompts/export. We will explicitly list the variables `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`, `KEYCLOAK_ADMIN_PASSWORD`, `KEYCLOAK_DATABASE_PASSWORD`, `LETS_ENCRYPT_EMAIL`, `AWS_ACCESS_KEY_ID`, and `AWS_SECRET_ACCESS_KEY`, ensuring each requested secret matches an exported environment variable.
+ **Documentation update:** Add a README note clarifying that credential values are collected interactively via `scripts/run-all.sh` and should not be stored in `config.yaml`.

## Risks / Trade-offs

- **[Secret leakage]** Storing credentials in `config.yaml` is risky, so we deliberately avoid reading them from config. → Document this constraint clearly and keep prompts centralized.
- **[YAML parsing failure]** The existing logic already reads non-sensitive values from `config.yaml`; keep that behavior untouched.

## Migration Plan

1. Remove any logic that reads credential values from `config.yaml`, keeping only the non-sensitive fields used for cluster configuration.
2. Refactor `prompt_secrets()` to iterate over a declarative list of secret definitions (name, env var, prompt message, allow-empty flag) so the exported variables mirror that list exactly.
3. Update `README.md` to describe that all credential secrets in `scripts/run-all.sh` are collected interactively and should not be stored in `config.yaml`.

## Open Questions

- None.
