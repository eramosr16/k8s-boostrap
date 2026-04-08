## ADDED Requirements

### Requirement: ArgoCD installation
The install script SHALL deploy ArgoCD to the K3s cluster using official Kubernetes manifests.

#### Scenario: ArgoCD namespace creation
- **WHEN** the script is executed
- **THEN** the `argocd` namespace SHALL be created if it doesn't exist

#### Scenario: ArgoCD deployment
- **WHEN** namespace is ready
- **THEN** ArgoCD SHALL be deployed using the official install manifest from ArgoCD docs

#### Scenario: ArgoCD service availability
- **WHEN** ArgoCD is deployed
- **THEN** the script SHALL wait for the argocd-server pod to be Ready

### Requirement: ArgoCD initial admin password
The script SHALL retrieve and display the initial admin password for the ArgoCD UI.

#### Scenario: Password retrieval
- **WHEN** ArgoCD is ready
- **THEN** the initial admin password SHALL be retrieved from Kubernetes secret

### Requirement: ArgoCD server exposure
The script SHALL expose the ArgoCD server service for local access.

#### Scenario: Port forwarding
- **WHEN** user runs the port-forward command
- **THEN** ArgoCD UI SHALL be accessible at http://localhost:8080