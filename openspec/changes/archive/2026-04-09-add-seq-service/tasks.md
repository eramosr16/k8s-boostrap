## 1. Seq Manifests

- [x] 1.1 Create Seq deployment manifest
- [x] 1.2 Create Seq service (ClusterIP)
- [x] 1.3 Create Seq persistent volume claim
- [x] 1.4 Create Seq secret for admin credentials

## 2. OpenTelemetry Configuration

- [x] 2.1 Update OpenTelemetry config to export logs to Seq

## 3. Traefik IngressRoute

- [x] 3.1 Create IngressRoute for Seq at logs.mydomain.com
- [x] 3.2 Configure TLS with certResolver: le

## 4. Verification

- [ ] 4.1 Verify Seq pod is running
- [ ] 4.2 Verify Seq is accessible at logs.mydomain.com
- [ ] 4.3 Test log ingestion from OTel