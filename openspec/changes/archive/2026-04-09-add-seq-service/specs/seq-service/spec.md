## ADDED Requirements

### Requirement: Seq receives logs from OpenTelemetry
Seq SHALL accept log data via HTTP from OpenTelemetry Collector.

#### Scenario: OTel sends logs to Seq
- **WHEN** OpenTelemetry Collector forwards logs to Seq HTTP endpoint
- **THEN** Seq stores and indexes the logs for searching

### Requirement: Seq is accessible at logs.mydomain.com
Seq SHALL be reachable externally via Traefik at logs.mydomain.com with TLS.

#### Scenario: User accesses Seq UI
- **WHEN** user navigates to https://logs.mydomain.com
- **THEN** Seq login page is displayed with HTTPS

### Requirement: Seq uses persistent storage
Seq SHALL use persistent volume for log data storage.

#### Scenario: Seq pod restarts
- **WHEN** Seq pod is restarted
- **THEN** logs are preserved on persistent volume

### Requirement: Seq admin credentials from secrets
Seq SHALL use admin credentials from Kubernetes secrets.

#### Scenario: Seq starts with credentials
- **WHEN** Seq container starts
- **THEN** admin email and password are read from environment variables mapped from secrets

## MODIFIED Requirements

(None)

## REMOVED Requirements

(None)