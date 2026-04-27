## Why

`run-all.sh` currently prompts for every credential even when most of those values already live in `config.yaml`. This makes the prompt logic inaccurate (e.g., LETS_ENCRYPT_EMAIL is sourced from the config), the number of prompts doesn’t match the number of exported secrets, and operators see blank prompts even when values could be autowired.

## What Changes

- Ensure `scripts/run-all.sh` compares missing secrets with `config.yaml` before prompting so only truly missing values are requested.
- Align exported environment variables with the actual set of prompts so everyone who runs the script receives the requested credentials explicitly.
- Document the change in `README.md` so maintainers understand which secrets come from `config.yaml` vs the interactive prompt.

## Capabilities

### New Capabilities
- `credential-prompt-validation`: Validate that each credential prompt in `scripts/run-all.sh` reflects data actually needed by the bootstrap process and respect values present in `config.yaml`.

### Modified Capabilities
- _None_

## Impact

- `scripts/run-all.sh` prompt logic and exported environment variable list will change slightly to match reality.
- `config.yaml` reading logic may expand to cover secrets like `traefik.email` and any others that should override prompts.
- Documentation (README) must note which values still require manual input so bootstrap runs stay predictable.

## Non-goals

- Replacing the interactive prompt system entirely (still needed for genuinely missing secrets).
- Moving credential storage out of `config.yaml` or into external secret management systems.
