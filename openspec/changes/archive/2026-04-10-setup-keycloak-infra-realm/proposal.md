## Why

Currently, Keycloak uses the `master` realm for all authentication. This mixes admin and service account identities, lacks proper separation for cluster operators, and requires all services to configure client credentials manually on each bootstrap. Creating a dedicated `infra` realm provides proper security boundary, automated client provisioning, and simplifies OIDC configuration for K3s API server.

## What Changes

- Create `infra` realm in Keycloak with proper OIDC configuration
- Configure K3s API server to use Keycloak as OIDC issuer via kube-apiserver flags
- Update Headlamp to authenticate against `infra` realm instead of `master`
- Update all services (Grafana, ArgoCD, Headlamp, Seq) to use `infra` realm clients
- Add realm initialization to run-all.sh bootstrap script
- Create service accounts with proper roles for cluster operations

## Capabilities

### New Capabilities

- `infra-realm`: Dedicated Keycloak realm for cluster services and operators
- `k3s-oidc`: K3s API server OIDC authentication with Keycloak infra realm
- `service-accounts`: Service accounts for cluster services (Grafana, ArgoCD, Headlamp, etc.)

### Modified Capabilities

- `keycloak-iam`: Update existing Keycloak setup to use infra realm as default

## Impact

- New: Keycloak realm configuration in run-all.sh
- Modified: K3s bootstrap needs kube-apiserver-arg flags
- Modified: Headlamp, Grafana, ArgoCD client configs point to infra realm
- Modified: All service deployments using OIDC authentication