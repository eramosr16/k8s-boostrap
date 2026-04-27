## Why

The `hello-world` application under `infra/applications` is no longer needed and adds noise to the ArgoCD root app, so removing it improves clarity and reduces maintenance surface.

## What Changes

- Remove the `infra/applications/hello-world` application directory and all references to it from ArgoCD applications and documentation.
- Ensure the root app manifests no longer reference the deleted application.
- Update onboarding docs to reflect the removal and note that the app is no longer deployed.
- Add specs capturing the removal plan so implementation steps are clear.

## Capabilities

### New Capabilities
- `hello-world-app-removal`: Define the requirements for safely deleting the `hello-world` application and ensuring ArgoCD no longer tries to deploy it.

### Modified Capabilities
- _None_

## Impact

- `infra/applications/hello-world/` directory will be deleted.
- ArgoCD manifests (root app or application directories) referencing the hello-world app must be updated or removed.
- Documentation (README or change logs) must note that the app has been removed so operators are not confused.

## Non-goals

- Keeping the `hello-world` app deployed or rewritten into another namespace.
- Touching other applications or services unless they explicitly reference the hello-world app.
