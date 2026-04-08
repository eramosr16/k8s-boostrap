## ADDED Requirements

### Requirement: ArgoCD root application watches infra directory
The ArgoCD root application SHALL watch the `infra/` directory and recursively deploy all YAML manifests contained within to the cluster.

#### Scenario: Deploy all manifests in infra directory
- **WHEN** a YAML manifest is added to `infra/services/` or `infra/applications/`
- **THEN** ArgoCD SHALL detect the change and deploy the manifest to the cluster

#### Scenario: Recursive directory scanning
- **WHEN** there are nested directories under `infra/`
- **THEN** ArgoCD SHALL traverse all subdirectories and deploy manifests found at any depth

#### Scenario: Existing manifests are deployed on initial sync
- **WHEN** the root-app is first synced to the cluster
- **THEN** all existing YAML manifests under `infra/` SHALL be deployed to their respective namespaces