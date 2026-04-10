## ADDED Requirements

### Requirement: All workloads have security context
All Kubernetes Deployments, StatefulSets, and DaemonSets SHALL have a security context configured.

#### Scenario: Deployment has security context
- **WHEN** a Deployment manifest is created or updated
- **THEN** it SHALL include `securityContext` with `runAsNonRoot: true`, `runAsUser: 1000`, and `fsGroup: 1000`

#### Scenario: DaemonSet has security context
- **WHEN** a DaemonSet manifest is created or updated
- **THEN** it SHALL include `securityContext` with `runAsNonRoot: true`, `runAsUser: 1000`, and `fsGroup: 1000`

#### Scenario: StatefulSet has security context
- **WHEN** a StatefulSet manifest is created or updated
- **THEN** it SHALL include `securityContext` with `runAsNonRoot: true`, `runAsUser: 1000`, and `fsGroup: 1000`