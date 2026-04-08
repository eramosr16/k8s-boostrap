## ADDED Requirements

### Requirement: K3s single-node cluster installation
The bootstrap script SHALL install K3s on a Linux host using the official install script.

#### Scenario: Fresh K3s installation
- **WHEN** the script is run on a system without K3s installed
- **THEN** K3s SHALL be installed and the service started

#### Scenario: Existing K3s installation
- **WHEN** the script is run on a system with K3s already installed
- **THEN** the script SHALL detect this and skip installation (idempotent)

#### Scenario: K3s service verification
- **WHEN** K3s installation completes
- **THEN** the script SHALL verify the service is running via `systemctl is-active k3s`

### Requirement: kubectl configuration
The bootstrap script SHALL configure kubectl to connect to the K3s cluster.

#### Scenario: kubectl config setup
- **WHEN** K3s is installed
- **THEN** kubectl SHALL be configured with the K3s cluster credentials from `/etc/rancher/k3s/k3s.yaml`

#### Scenario: kubeconfig permissions
- **WHEN** kubeconfig is copied to user home
- **THEN** the script SHALL set appropriate file permissions (600)