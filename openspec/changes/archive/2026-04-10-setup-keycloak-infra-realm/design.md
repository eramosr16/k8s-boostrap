## Context

Currently, the cluster uses Keycloak's `master` realm for all OIDC authentication. Services like Grafana, ArgoCD, and Headlamp each create their own clients in master realm, making it hard to manage cluster-wide permissions. K3s API server is not configured for OIDC, so users must use client certificates or kubeconfig files.

## Goals / Non-Goals

**Goals:**
- Create dedicated `infra` realm for cluster services and operator authentication
- Configure K3s API server with OIDC flags pointing to Keycloak infra realm
- Enable Headlamp users to authenticate via Keycloak and access Kubernetes API
- Migrate all service clients (Grafana, ArgoCD, Headlamp) to infra realm

**Non-Goals:**
- Modify existing user passwords or credentials in master realm
- Enable LDAP or other identity providers
- Set up multi-cluster OIDC federation

## Decisions

1. **Realm creation**: Use `kcadm` in run-all.sh after Keycloak is ready
   - Alternative: Import realm from JSON export - more error-prone
   - Chosen: kcadm allows validation and incremental updates

2. **K3s OIDC configuration**: Use K3s config file with kube-apiserver-arg flags
   - Alternative: Command-line flags in /etc/systemd/system/k3s.service - harder to maintain
   - Chosen: YAML config at /etc/rancher/k3s/k3s.yaml is K3s-native

3. **Client names**: Use realm-specific prefixes (e.g., `infra-grafana`, `infra-argocd`)
   - Keeps clients organized and prevents conflicts with master realm

4. **Service account approach**: Create service accounts in realm with service-account-enabled flag
   - Each service gets client ID + secret stored as Kubernetes secret

## Risks / Trade-offs

- [Risk] OIDC configuration changes require K3s restart → Schedule maintenance window
- [Risk] Token expiry - Keycloak tokens expire → Use refresh tokens, set appropriate timeout
- [Risk] Realm setup failure breaks bootstrap → Add retry logic with clear error messages

## Migration Plan

1. Add realm creation function to run-all.sh after Keycloak is ready
2. Create `infra` realm with OIDC enabled
3. Create clients for each service (k3s-api, grafana, argocd, headlamp, seq)
4. Configure K3s with OIDC kube-apiserver-arg flags
5. Restart K3s to apply OIDC configuration
6. Update service deployments to use new client credentials