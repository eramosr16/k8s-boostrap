## ADDED Requirements

### Requirement: Credential prompts remain the single source of truth
`scripts/run-all.sh` SHALL treat `prompt_secrets()` as the only source for sensitive credentials and must not read those values from `config.yaml` so secrets are never stored in git.

#### Scenario: prompt always requests credentials
- **WHEN** the script runs even if the config file contains placeholders
- **THEN** each credential prompt appears, ensuring values are collected interactively rather than inherited from `config.yaml`

### Requirement: Exported credentials align with prompts
Every environment variable exported for secret creation in `scripts/run-all.sh` SHALL have a corresponding prompt entry, ensuring no variable is exported without being collected.

#### Scenario: secret export list matches prompt list
- **WHEN** the script enumerates credential definitions
- **THEN** each exported variable name appears exactly once in the prompt list, and the script errors if a definition is missing from either list
