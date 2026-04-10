## ADDED Requirements

### Requirement: All containers use Always image pull policy
All containers in Deployments, StatefulSets, and DaemonSets SHALL have `imagePullPolicy: Always`.

#### Scenario: Deployment containers use Always policy
- **WHEN** a Deployment container image is specified
- **THEN** it SHALL include `imagePullPolicy: Always`

#### Scenario: DaemonSet containers use Always policy
- **WHEN** a DaemonSet container image is specified
- **THEN** it SHALL include `imagePullPolicy: Always`

#### Scenario: StatefulSet containers use Always policy
- **WHEN** a StatefulSet container image is specified
- **THEN** it SHALL include `imagePullPolicy: Always`