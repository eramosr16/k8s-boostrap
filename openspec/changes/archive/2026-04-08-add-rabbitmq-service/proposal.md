## Why

The README already references `broker/rabbitmq.yaml` in the directory structure, indicating RabbitMQ is planned as part of the platform services. Adding RabbitMQ will provide message queue capabilities for asynchronous processing, event-driven architectures, and task scheduling between microservices.

## What Changes

- Add RabbitMQ Kubernetes manifests in `infra/services/broker/rabbitmq/`
- Create Deployment with RabbitMQ container
- Create Service (ClusterIP) for internal access
- Create Secret with username/password placeholders (RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS)
- Add PersistentVolumeClaim for message persistence
- Update README.md with RabbitMQ connection details and secrets management

## Capabilities

### New Capabilities
- `rabbitmq-service`: Message broker service with persistent storage and credential management

### Modified Capabilities
- None

## Impact

- New directory: `infra/services/broker/rabbitmq/`
- Updated: `README.md` (service connection details, secrets table)

## Non-goals

- High-availability clustering (single node for now)
- RabbitMQ management UI exposed externally
- Pre-configured exchanges or queues