## ADDED Requirements

### Requirement: Cluster configuration file stores non-sensitive values
The `config.yaml` file SHALL store all non-sensitive configuration values used across cluster manifests.

#### Scenario: Config file exists
- **WHEN** user creates `config.yaml` in repository root
- **THEN** file SHALL be valid YAML with configurable values

#### Scenario: Config contains cluster domain
- **WHEN** config is loaded
- **THEN** config SHALL include `cluster_domain` field (default: `cluster.local`)

#### Scenario: Config contains Traefik email
- **WHEN** config is loaded
- **THEN** config SHALL include `traefik_email` field for Let's Encrypt ACME

#### Scenario: Config contains image tags
- **WHEN** config is loaded
- **THEN** config SHALL include `image_tags` section with versioned tags for each service

### Requirement: run-all.sh reads config file
The bootstrap script SHALL read config values before deploying manifests.

#### Scenario: Config file exists
- **WHEN** user runs `./scripts/run-all.sh`
- **THEN** script SHALL check for `config.yaml` and load values if present

#### Scenario: Config values used for placeholders
- **WHEN** config is loaded
- **THEN** script SHALL use values to populate placeholders in manifest templates

#### Scenario: Config missing values
- **WHEN** config is missing a value
- **THEN** script SHALL use default values or prompt user

### Requirement: Placeholder replacement works
The script SHALL replace placeholders in manifests with values from config.

#### Scenario: Placeholders in manifests
- **WHEN** manifests contain placeholders like `{{CLUSTER_DOMAIN}}`
- **THEN** script SHALL replace with values from config before applying

#### Scenario: Placeholder format
- **WHEN** script processes manifests
- **THEN** placeholders SHALL use double-brace format `{{VALUE}}` to avoid conflicts