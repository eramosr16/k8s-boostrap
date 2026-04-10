## ADDED Requirements

### Requirement: K3s server configuration via config.yaml
The system SHALL support K3s server configuration options through the `config.yaml` file, allowing users to customize their K3s installation before bootstrapping.

#### Scenario: Default K3s installation
- **WHEN** `config.yaml` does not have a `k3s` section
- **THEN** K3s is installed with default options (single server, Traefik enabled)

#### Scenario: Custom K3s server flags
- **WHEN** `config.yaml` contains a `k3s` section with custom `serverFlags`
- **THEN** K3s is installed using the provided flags via `INSTALL_K3S_EXEC`

#### Scenario: Disabling embedded components
- **WHEN** `config.yaml` specifies `disable` options (e.g., traefik, servicelb)
- **THEN** K3s is installed with those components disabled

### Requirement: Config file validation
The system SHALL validate the K3s configuration section in `config.yaml` and warn users about invalid options.

#### Scenario: Invalid configuration option
- **WHEN** `config.yaml` contains an unknown K3s option
- **THEN** A warning is displayed during bootstrap but installation continues with defaults

### Requirement: Documentation of available options
The system SHALL document all supported K3s configuration options in README.md.

#### Scenario: User reviews available options
- **WHEN** User reads README.md K3s configuration section
- **THEN** They can see all available options with their default values