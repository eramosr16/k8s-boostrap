## ADDED Requirements

### Requirement: Headlamp dashboard is accessible via ingress
The system SHALL provide access to the Headlamp web interface via the ingress at `headlamp.mydomain.com`.

#### Scenario: Access via ingress
- **WHEN** user navigates to `https://headlamp.mydomain.com`
- **THEN** the Headlamp web interface is displayed

### Requirement: Headlamp authenticates using service account token
The system SHALL authenticate users via a service account token for secure cluster access.

#### Scenario: Token authentication
- **WHEN** user logs in with the service account token
- **THEN** Headlamp grants access based on the service account's RBAC permissions

### Requirement: Headlamp has cluster-wide read access
The system SHALL provide Headlamp with read access to all Kubernetes resources in the cluster.

#### Scenario: View cluster resources
- **WHEN** user views cluster resources in Headlamp
- **THEN** all namespaces and resources are visible based on RBAC

### Requirement: Headlamp uses ClusterIP service
The system SHALL expose Headlamp via a ClusterIP service on port 80 (mapped to container port 4466).

#### Scenario: Service connectivity
- **WHEN** traffic is sent to the headlamp service
- **THEN** requests are forwarded to the Headlamp pod on port 4466