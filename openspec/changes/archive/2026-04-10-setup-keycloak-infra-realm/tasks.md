## 1. Update run-all.sh - Realm Creation

- [x] 1.1 Add create_keycloak_infra_realm() function
- [x] 1.2 Create infra realm with kcadm
- [x] 1.3 Configure realm OIDC settings
- [x] 1.4 Add realm creation to main flow after Keycloak ready

## 2. Create infra realm Clients

- [x] 2.1 Create k3s-api client for API server OIDC
- [x] 2.2 Create Grafana client (infra-grafana)
- [x] 2.3 Create ArgoCD client (infra-argocd)
- [x] 2.4 Create Headlamp client (infra-headlamp)
- [x] 2.5 Create Seq client (infra-seq)

## 3. Configure K3s OIDC

- [x] 3.1 Add kube-apiserver-arg configuration to K3s config
- [x] 3.2 Test OIDC configuration after K3s restart
- [x] 3.3 Create ClusterRoleBinding for admin users

## 4. Update Services to use infra realm

- [x] 4.1 Update Keycloak client config for Headlamp
- [x] 4.2 Update Grafana OIDC secret to use infra realm
- [x] 4.3 Update ArgoCD OIDC config to use infra realm
- [x] 4.4 Test all service authentications

## 5. Testing

- [ ] 5.1 Verify realm created in Keycloak
- [ ] 5.2 Verify all clients exist
- [ ] 5.3 Test Headlamp login with infra realm
- [ ] 5.4 Test kubectl with Keycloak token