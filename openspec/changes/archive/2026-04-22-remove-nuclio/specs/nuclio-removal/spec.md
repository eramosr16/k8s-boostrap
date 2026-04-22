## REMOVED Requirements

### Requirement: Remove nuclio configuration
All Nuclio serverless platform references SHALL be removed from the infrastructure.

#### Scenario: Remove config.yaml nuclio entries
- **WHEN** config.yaml is loaded
- **THEN** there is no `nuclio:` section, no `images.nuclio`, and no `routes.nuclio`

#### Scenario: Remove run-all.sh nuclio code
- **WHEN** run-all.sh is executed
- **THEN** there is no `install_nuclio` function and no nuclio route loading

#### Scenario: Remove nuclio service directory
- **WHEN** the filesystem is inspected
- **THEN** `infra/services/nuclio/` directory does not exist

#### Scenario: Keep applications namespace
- **WHEN** the applications directory is inspected
- **THEN** `infra/applications/` directory and namespace manifest exist