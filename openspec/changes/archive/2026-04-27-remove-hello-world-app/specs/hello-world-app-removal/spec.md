## ADDED Requirements

### Requirement: Remove hello-world application directory
The repository SHALL delete the `infra/applications/hello-world/` directory and all files it contains so the obsolete sample application is no longer tracked.

#### Scenario: Repository tree omits hello-world
- **WHEN** reviewing the `infra/applications` directory after the change
- **THEN** the `hello-world` directory is absent and git status shows no files under that path

### Requirement: ArgoCD configuration no longer references hello-world
The ArgoCD root application and any nested `applications/*` manifests SHALL drop the `hello-world` entry so synchronization does not expect the deleted app.

#### Scenario: ArgoCD sync succeeds without hello-world
- **WHEN** the updated root app manifest is applied to ArgoCD after removing the directory
- **THEN** `argocd app get <root-app>` reports all remaining applications healthy and there is no `hello-world` entry in the application list

### Requirement: Documentation records the removal
The main README SHALL include a short note stating that the `hello-world` application was intentionally removed to keep the GitOps tree minimal.

#### Scenario: README lists the removal
- **WHEN** scanning README recent updates after the change
- **THEN** there is a new bullet referencing the removal of `infra/applications/hello-world`
