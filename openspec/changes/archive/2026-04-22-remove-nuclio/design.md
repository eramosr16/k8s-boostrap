## Context

The Kubernetes bootstrap infrastructure includes Nuclio serverless platform which is no longer needed. This design covers the removal of all Nuclio-related configuration and resources while keeping the infrastructure working.

**Current State:**
- `config.yaml` contains nuclio image version, routes, and helm configuration
- `scripts/run-all.sh` contains nuclio installation and route loading
- `infra/services/nuclio/` directory contains namespace, helm chart, ingress, middleware, RBAC, and values

## Goals / Non-Goals

**Goals:**
- Remove all nuclio references from config.yaml
- Remove nuclio installation from run-all.sh
- Delete infra/services/nuclio/ directory
- Keep infrastructure services operational (PostgreSQL, Redis, Keycloak, RabbitMQ, Grafana, etc.)

**Non-Goals:**
- Do not modify any other infrastructure services
- Do not add new capabilities
- Do not touch applications folder structure (keep namespace only as per user request)

## Decisions

1. **Remove vs leave unused**: Delete all nuclio files entirely rather than leaving commented code. This reduces confusion and maintenance burden.

2. **Order of removal**: 
   - First remove config.yaml references
   - Then remove run-all.sh code
   - Finally delete the nuclio service directory

3. **No rollback needed**: This is a simple removal with no runtime state - no data migration or rollback strategy required.

## Risks / Trade-offs

- **No risks identified**: This is a straightforward removal with no dependencies on other services.