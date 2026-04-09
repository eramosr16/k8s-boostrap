## Context

Seq is a centralized log aggregation platform that provides structured logging and search capabilities. It integrates with OpenTelemetry to consume logs via HTTP. The service will be exposed publicly at logs.mydomain.com.

## Goals / Non-Goals

**Goals:**
- Deploy Seq in infra namespace with persistent storage
- Configure OpenTelemetry to forward logs to Seq
- Expose Seq via Traefik at logs.mydomain.com with TLS

**Non-Goals:**
- Complex authentication setup (basic admin credentials)
- Log retention policies

## Decisions

1. **Image**: Use official Seq Docker image (datalust/seq:latest)

2. **Data Storage**: Use PVC for persistent log storage

3. **Log Ingestion**: Configure OTel collector to send logs to Seq HTTP endpoint (port 5341)

4. **Ingress**: Follow existing pattern from grafana-ingressroute.yaml and keycloak-ingressroute.yaml

5. **Credentials**: Use environment variables (SEQ_ADMIN_EMAIL, SEQ_ADMIN_PASSWORDKEY) - password from secret

## Risks / Trade-offs

- [Risk] Seq requires significant storage → Mitigation: Monitor storage usage, implement retention
- [Risk] Public exposure of logs → Mitigation: Use HTTPS/TLS, strong admin password

## Migration Plan

1. Create Seq manifests (deployment, service, pvc, secret)
2. Configure OTel to export logs to Seq
3. Create Traefik IngressRoute
4. Deploy and verify

## Open Questions

- What retention period should be configured?
- Should we enable Seq's built-in authentication requiring API keys?