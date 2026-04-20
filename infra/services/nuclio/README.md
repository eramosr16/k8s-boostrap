# Nuclio Service

Serverless functions platform for Kubernetes.

## Overview

Nuclio is a high-performance serverless framework. This service deploys the Nuclio controller and dashboard to the cluster.

## Components

- **Namespace**: `nuclio`
- **Controller**: Manages function CRDs
- **Dashboard**: Web UI for function management
- **Platform Config**: ConfigMap with logging, metrics, and broker settings

## Configuration

### config.yaml

```yaml
nuclio:
  helm:
    repo: https://nuclio.github.io/nuclio/charts
  registry:
    ecr: ""  # ECR URL for function images
  rabbitmq:
    url: "amqp://rabbitmq.infra.svc.cluster.local:5672"

routes:
  nuclio: nuclio
```

### values.yaml

Key settings for the Helm chart:

- `controller.namespace`: Set to `nuclio` for single-tenant
- `dashboard.containerBuilderKind`: Use `kaniko` for secure image building
- `registry.pushPullUrl`: Your container registry URL

### Platform Configuration

The `platform-config.yaml` ConfigMap configures:

- **Logger**: stdout sink for function logs
- **Metrics**: Prometheus pull on port 8090
- **Health Check**: Port 8082
- **Web Admin**: Port 8081
- **Broker**: Uses RabbitMQ from infra namespace

## Metrics Integration

- ServiceMonitor: `infra/services/nuclio/servicemonitor.yaml`
- Metrics port: 8090
- Scraped by Prometheus in `infra` namespace

## Usage

### Access Dashboard

```
kubectl -n nuclio port-forward svc/nuclio-ingress 8080:8080
```

Then open http://localhost:8080

### Deploy a Function

```yaml
apiVersion: nuclio.io/v1alpha1
kind: Function
metadata:
  name: my-function
  namespace: nuclio
spec:
  image: my-registry.io/my-function:latest
  handler: main:handler
  runtime: python
```

### RabbitMQ Trigger

Functions can subscribe to RabbitMQ queues:

```yaml
spec:
  triggers:
    rabbitmq:
      kind: rabbitmq
      url: amqp://rabbitmq.infra.svc.cluster.local:5672
      queueName: my-queue
```

## Version Freeze

For production, pin versions in `values.yaml`:

```yaml
controller:
  image:
    tag: 1.12.5
dashboard:
  image:
    tag: 1.12.5
```

Test upgrades in dev before applying to production.