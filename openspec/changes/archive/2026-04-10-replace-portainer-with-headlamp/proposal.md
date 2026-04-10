## Why

Portainer has become a legacy solution for cluster management. Headlamp is a modern, Kubernetes-native dashboard that provides better integration with the Kubernetes API and a more active development community. Replacing Portainer with Headlamp will provide a more up-to-date and Kubernetes-focused management interface.

## What Changes

- Remove Portainer deployment, service, PVC, secret, and ingress from `infra/services/observability/portainer/`
- Add Headlamp deployment, service, and ingress to `infra/services/observability/headlamp/`
- Update README.md to reflect the change from Portainer to Headlamp
- Update any references in documentation

## Capabilities

### New Capabilities
- `headlamp-dashboard`: Kubernetes-native web-based cluster management dashboard

### Modified Capabilities
- None - this is a direct replacement of one dashboard tool with another

## Non-goals

- Adding additional dashboard features beyond basic Headlamp functionality
- Migrating existing Portainer data (configuration will be fresh)

## Impact

- Remove all files in `infra/services/observability/portainer/`
- Add new files in `infra/services/observability/headlamp/`
- Update `README.md` references