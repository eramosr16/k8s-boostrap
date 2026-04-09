## 1. OpenTelemetry Collector Deployment

- [x] 1.1 Create OpenTelemetry Collector namespace or use infra namespace
- [x] 1.2 Create OpenTelemetry Collector ConfigMap with receivers, processors, exporters
- [x] 1.3 Create OpenTelemetry Collector Deployment manifest
- [x] 1.4 Create OpenTelemetry Collector Service (ClusterIP for internal access)

## 2. Grafana Datasource Configuration

- [x] 2.1 Update Grafana datasource ConfigMap to add OpenTelemetry
- [x] 2.2 Configure OTLP endpoint for Grafana datasource

## 3. Verification

- [ ] 3.1 Verify OpenTelemetry Collector pod is running
- [ ] 3.2 Verify Grafana can connect to OpenTelemetry datasource
- [ ] 3.3 Test trace queries in Grafana Explore