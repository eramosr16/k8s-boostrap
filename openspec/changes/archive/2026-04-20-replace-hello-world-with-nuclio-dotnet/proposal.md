## Why

The current hello-world example uses a basic HTTP server. Replacing it with a Nuclio serverless function demonstrates the platform's function-as-a-service capabilities and provides a more realistic example of how to deploy serverless functions on the cluster.

## What Changes

- Remove the existing hello-world application manifests
- Add a new hello-world function using .NET Core 9.0 runtime
- Include all necessary files: handler code, project file, Dockerfile, and function specification

## Capabilities

### New Capabilities

- `hello-world`: Serverless hello-world function using Nuclio .NET Core 9.0 runtime

### Modified Capabilities

- None

## Impact

- File: `infra/applications/hello-world/` - replaced with nuclio function files
