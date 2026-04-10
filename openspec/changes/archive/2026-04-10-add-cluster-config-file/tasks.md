## 1. Create config.yaml

- [ ] 1.1 Create `config.yaml` in repository root
- [ ] 1.2 Add `cluster` section with domain and Traefik email
- [ ] 1.3 Add `images` section with versioned tags for each service

## 2. Update run-all.sh

- [ ] 2.1 Add config loading function
- [ ] 2.2 Add placeholder replacement logic using envsubst or sed
- [ ] 2.3 Add fallback for missing config values
- [ ] 2.4 Test config loading

## 3. Update Manifest Placeholders

- [ ] 3.1 Update traefik-config.yaml to use {{TRAEFIK_EMAIL}}
- [ ] 3.2 Update services to use {{CLUSTER_DOMAIN}}
- [ ] 3.3 Update image tags to use {{IMAGE_TAG}}

## 4. Documentation

- [ ] 4.1 Update README.md with config file usage