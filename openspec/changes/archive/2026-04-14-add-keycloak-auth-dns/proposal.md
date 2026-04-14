## Why

Keycloak clients deployed in this cluster are trying to validate tokens over the public-facing `auth.<domain>` hostname. The extra hop out to the public network and back introduces delays and intermittent timeouts, which breaks service-to-service authentication. Providing a stable internal DNS alias that points directly at the Keycloak service removes the dependency on external routing and keeps authentication traffic on the cluster network.

## What Changes

- Add a static host entry to the CoreDNS configuration so that `auth.<cluster-domain>` resolves to the Keycloak service IP and ties directly into the cluster DNS cache.
- Teach `config.yaml` to accept the Kubernetes service IP that should back `auth.<cluster-domain>` and make the automated bootstrap script (`scripts/run-all.sh`) write that entry into `/etc/coredns/NodeHosts` as part of the Keycloak deployment flow.
- Document the additional configuration requirement in the repository README so future clusters know to align the CoreDNS alias with the Keycloak route.

## Capabilities

### New Capabilities
- `keycloak-auth-dns`: Ensures the auth-facing hostname used by services resolves internally by seeding CoreDNS with the Keycloak service IP and wiring the bootstrap script to propagate the mapping during deployment.

### Modified Capabilities
<!-- None: no spec-level behavior changes are required. -->

## Impact

- `infra/services/registry/` (CoreDNS manifest) needs the new host entry.
- `scripts/run-all.sh` must write the alias as part of the Keycloak bootstrap/Keycloak readiness block.
- `config.yaml` gains a new value so the bootstrap script knows which IP to register.
- `README.md` is updated to mention the alias requirement and how to configure it.

## Non-goals

- Automatically discovering the Keycloak service IP from the cluster: the IP will still need to be supplied via `config.yaml`.
- Modifying Keycloak itself or its external DNS records; this change only affects internal CoreDNS bookkeeping.
