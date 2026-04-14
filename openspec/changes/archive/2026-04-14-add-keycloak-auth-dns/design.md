## Context

CoreDNS currently resolves intra-cluster hostnames via the `hosts` plugin and an external `NodeHosts` file (`infra/services/registry/corefile.yaml`). When services use `auth.<cluster-domain>` they hit the public ingress address, which adds latency and occasionally causes Keycloak token validations to timeout because the call exits the cluster and re-enters. The `scripts/run-all.sh` bootstrap script seeds the same `NodeHosts` file with static entries for developer tooling, but it does not yet cover the auth domain. A repeatable bootstrap flow needs to write the desired alias every time the cluster is deployed.

## Goals / Non-Goals

**Goals:**
- Guarantee that `auth.<cluster-domain>` resolves to the internal Keycloak service IP by updating `NodeHosts` and the CoreDNS manifest.
- Teach `config.yaml` how to store the Keycloak service IP for this alias and let `scripts/run-all.sh` write the updated `NodeHosts` entry so the bootstrap between runs remains consistent.
- Document the requirement in the README so operators know to keep the alias in sync whenever the Keycloak service IP changes.

**Non-Goals:**
- Discovering the Keycloak service IP dynamically at runtime (the IP must be provided via `config.yaml`).
- Changing external DNS/ingress configuration for `auth.<domain>`; this work only keeps the internal CoreDNS alias aligned.

## Decisions

1. **Write the alias via `NodeHosts` rather than modifying the static CoreDNS ConfigMap directly.** NodeHosts already stores the `/etc/coredns/NodeHosts` entries that CoreDNS uses, and the bootstrap script already regenerates it for local tooling. Using the same file keeps the change limited to one place and avoids coordinating rolling restarts of the CoreDNS deployment.

2. **Treat the Keycloak service IP as a configuration value.** Hard-coding the IP in code would break when the service is re-created, so we will add a new field (e.g., `cluster.hostIP`) in `config.yaml` and pass it to `run-all.sh`. The script will respect the configured IP (erroring if missing) and drop an entry that looks like `<ip> auth.<cluster-domain>` alongside the existing host entries.

3. **Only seed the alias after Keycloak is deployed.** To avoid races, the script should append the entry when the Keycloak clients and services are configured (immediately after `configure_k3s_oidc` or a similar point where the service already exists) and then reload the CoreDNS ConfigMap if necessary.

## Risks / Trade-offs

[Risk] → If the Keycloak service IP changes, DNS will break until `config.yaml` is updated and the bootstrap script runs again. → Mitigation: add clear README instructions and validation in `scripts/run-all.sh` that warns when the service IP differs from the configured value.

[Risk] → Writing to `/etc/coredns/NodeHosts` requires permissions; failing to persist the entry means services continue hitting the public hostname. → Mitigation: run the script as root (the bootstrap already does this) and verify the file contains the alias after the script runs.

## Migration Plan

1. Extend `config.yaml` with a `hostIP` value and update `scripts/run-all.sh` to read it when building the NodeHosts entry.
2. Add the host line to the CoreDNS manifests under `infra/services/registry/` so the entry exists in the GitOps config and matches what the script writes.
3. Ensure the bootstrap script explicitly writes `<hostIP> auth.<cluster-domain>` to `/etc/coredns/NodeHosts` before reloading CoreDNS or restarting the cluster bootstrapping flow.
4. Update README to call out the new configuration requirement so operators know to keep the value accurate.

## Open Questions

- Should the bootstrap script confirm that the alias matches the service IP returned by `kubectl get svc keycloak` (and warn if it differs)?
- Do other services need similar static aliases, or is this change limited to the Keycloak auth host?
