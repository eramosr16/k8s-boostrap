## Context

The hello-world application uses a simple HTTP server. Replacing it with a Nuclio function demonstrates serverless deployment and provides a more production-realistic example.

## Goals / Non-Goals

**Goals:**
- Deploy a Nuclio .NET Core 9.0 function as a replacement for hello-world
- Maintain the same interface (HTTP GET returns "Hello, from nuclio")

**Non-Goals:**
- Add any advanced Nuclio features (triggers, scaling policies, etc.)
- Migrate other applications to Nuclio

## Decisions

- **.NET Core 9.0**: Current LTS version with modern features
- **Docker-based deployment**: Standard Nuclio approach for custom runtimes
- **Empty handler**: Simple implementation matching original hello-world behavior

## Risks / Trade-offs

- Nuclio runtime requires the Nuclio platform to be installed on the cluster (low risk - assumed already present)
- .NET Core 9.0 increases container image size compared to minimal images