## 1. Remove Nuclio Configuration

- [x] 1.1 Remove `images.nuclio` from config.yaml
- [x] 1.2 Remove `routes.nuclio` from config.yaml
- [x] 1.3 Remove entire `nuclio:` section from config.yaml

## 2. Remove Nuclio from run-all.sh

- [x] 2.1 Remove `ROUTE_NUCLIO` loading code
- [x] 2.2 Remove `NUCLIO_HELM_REPO` loading code
- [x] 2.3 Remove `NUCLIO_ECR` loading code
- [x] 2.4 Remove `NUCLIO_RABBITMQ_URL` loading code
- [x] 2.5 Remove `install_nuclio` function
- [x] 2.6 Remove `install_nuclio` call from main()

## 3. Remove Nuclio Service Directory

- [x] 3.1 Delete `infra/services/nuclio/` directory

## 4. Verify Changes

- [x] 4.1 Verify no remaining nuclio references in config.yaml
- [x] 4.2 Verify no remaining nuclio references in run-all.sh
- [x] 4.3 Verify `infra/services/nuclio/` is deleted
- [x] 4.4 Verify `infra/applications/` still exists with namespace