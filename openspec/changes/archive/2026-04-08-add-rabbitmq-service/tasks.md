## 1. Create RabbitMQ manifests

- [x] 1.1 Create infra/services/broker/rabbitmq/ directory
- [x] 1.2 Create rabbitmq-secret.yaml with RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS
- [x] 1.3 Create rabbitmq-deployment.yaml with rabbitmq:3-management image
- [x] 1.4 Create rabbitmq-service.yaml (ClusterIP on port 5672)
- [x] 1.5 Create rabbitmq-pvc.yaml for data persistence

## 2. Update documentation

- [x] 2.1 Add RabbitMQ to README.md service connection table
- [x] 2.2 Add RabbitMQ secrets to README.md secrets table