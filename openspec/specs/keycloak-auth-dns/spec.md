## ADDED Requirements

### Requirement: Internal alias for auth domain
The system SHALL ensure CoreDNS resolves `auth.<cluster-domain>` to the Keycloak service IP by keeping the host entry `<hostIP> auth.<cluster-domain>` in both the GitOps manifest under `infra/services/registry/` and `/etc/coredns/NodeHosts`.

#### Scenario: CoreDNS returns Keycloak IP
- **WHEN** ArgoCD syncs the CoreDNS manifest after the change is deployed
- **THEN** CoreDNS loads a host entry that resolves `auth.<cluster-domain>` to the configured Keycloak IP and service-to-service calls use that internal address

### Requirement: Bootstrap script propagates alias
The automated bootstrap script SHALL write the same host entry to `/etc/coredns/NodeHosts` immediately after the Keycloak service is ready, so a fresh cluster installation populates CoreDNS with the alias before services depend on it.

#### Scenario: run-all.sh applies alias
- **WHEN** `./scripts/run-all.sh` completes the Keycloak bootstrap steps
- **THEN** `/etc/coredns/NodeHosts` contains `<hostIP> auth.<cluster-domain>` and CoreDNS reloads if necessary so DNS queries for the auth host resolve without external hops

### Requirement: Config enforces Keycloak IP value
The bootstrap configuration SHALL provide a `hostIP` value that the script uses when writing host entries, and the script SHALL exit with an error if the value is missing or empty.

#### Scenario: Missing configuration
- **WHEN** `./scripts/run-all.sh` runs without `hostIP` set in `config.yaml`
- **THEN** the script exits early with an error message explaining that the field is required before the alias can be written
