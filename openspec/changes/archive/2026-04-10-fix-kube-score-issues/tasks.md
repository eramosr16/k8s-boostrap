## 1. Loki StatefulSet

- [x] 1.1 Add serviceName to Loki StatefulSet
- [x] 1.2 Add security context to Loki container
- [x] 1.3 Add imagePullPolicy: Always to Loki container
- [x] 1.4 Add ephemeral-storage limits to Loki container

## 2. Promtail DaemonSet

- [x] 2.1 Add security context to Promtail container
- [x] 2.2 Add imagePullPolicy: Always to Promtail container
- [x] 2.3 Add ephemeral-storage limits to Promtail container

## 3. PostgreSQL

- [x] 3.1 Add security context to postgres container
- [x] 3.2 Add imagePullPolicy: Always to postgres container
- [x] 3.3 Add ephemeral-storage limits to postgres container

## 4. Redis

- [x] 4.1 Add security context to redis container
- [x] 4.2 Add imagePullPolicy: Always to redis container
- [x] 4.3 Add ephemeral-storage limits to redis container

## 5. RabbitMQ

- [x] 5.1 Add security context to rabbitmq container
- [x] 5.2 Add imagePullPolicy: Always to rabbitmq container
- [x] 5.3 Add ephemeral-storage limits to rabbitmq container

## 6. Keycloak

- [x] 6.1 Add security context to keycloak container
- [x] 6.2 Add imagePullPolicy: Always to keycloak container
- [x] 6.3 Add ephemeral-storage limits to keycloak container
- [x] 6.4 Fix duplicate liveness/readiness probes (use different port for liveness)

## 7. Prometheus

- [x] 7.1 Add security context to prometheus container
- [x] 7.2 Add imagePullPolicy: Always to prometheus container
- [x] 7.3 Add ephemeral-storage limits to prometheus container

## 8. Grafana

- [x] 8.1 Add security context to grafana container
- [x] 8.2 Add imagePullPolicy: Always to grafana container
- [x] 8.3 Add ephemeral-storage limits to grafana container

## 9. OpenTelemetry

- [x] 9.1 Add security context to otel-collector container
- [x] 9.2 Add imagePullPolicy: Always to otel-collector container
- [x] 9.3 Add ephemeral-storage limits to otel-collector container
- [x] 9.4 Fix duplicate liveness/readiness probes

## 10. Headlamp

- [x] 10.1 Add security context to headlamp container
- [x] 10.2 Add imagePullPolicy: Always to headlamp container
- [x] 10.3 Add ephemeral-storage limits to headlamp container
- [x] 10.4 Fix duplicate liveness/readiness probes

## 11. Hello World App

- [x] 11.1 Add security context to hello-world container
- [x] 11.2 Add imagePullPolicy: Always to hello-world container
- [x] 11.3 Add ephemeral-storage limits to hello-world container

## 12. Verify Fixes

- [x] 12.1 Run kube-score to verify all issues are fixed