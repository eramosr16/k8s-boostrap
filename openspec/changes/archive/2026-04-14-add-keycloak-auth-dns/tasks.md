## 1. Configuration and defaults

- [x] 1.1 Extend `config.yaml` with a `hostIP` entry and describe how to pick the correct service IP in the comment block for cluster/domain settings.
- [x] 1.2 Ensure `scripts/run-all.sh` reads `hostIP` from the centralized configuration during `load_cluster_config` and exports it for downstream functions.

## 2. Bootstrap automation

- [x] 2.1 Fail fast when `hostIP` is empty by checking the value before touching `/etc/coredns/NodeHosts`.
- [x] 2.2 Append `<hostIP> auth.<CLUSTER_DOMAIN>` to `/etc/coredns/NodeHosts` once Keycloak clients are configured so that the alias exists before services rely on it.
- [x] 2.3 Reload (or signal) CoreDNS if necessary so the new NodeHosts entry takes effect without manual intervention.

## 3. CoreDNS manifests

- [x] 3.1 Update `infra/services/registry/` CoreDNS manifest(s) to include the same host line for `auth.<cluster-domain>` so the GitOps config matches what the bootstrap script writes.
- [x] 3.2 Verify the manifest entry mirrors the configured IP and does not conflict with existing entries (e.g., remove duplicate host lines).

## 4. Documentation

- [x] 4.1 Document the new alias requirement in `README.md`, describing how to keep `hostIP` in sync with the Keycloak service.
