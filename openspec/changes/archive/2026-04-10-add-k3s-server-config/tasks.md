## 1. Add K3s configuration to config.yaml

- [x] 1.1 Add `k3s` section to `config.yaml` with default values
- [x] 1.2 Include common K3s options: disable flags, server flags, cluster domain

## 2. Update bootstrap.sh to read K3s config

- [x] 2.1 Modify `scripts/bootstrap.sh` to read k3s config from config.yaml
- [x] 2.2 Add function to parse config.yaml for k3s section
- [x] 2.3 Apply config via INSTALL_K3S_EXEC environment variable

## 3. Update documentation

- [x] 3.1 Document K3s configuration options in README.md
- [x] 3.2 Add example config.yaml k3s section

## 4. Verify implementation

- [x] 4.1 Test bootstrap.sh with default config (no k3s section)
- [x] 4.2 Test bootstrap.sh with custom k3s config