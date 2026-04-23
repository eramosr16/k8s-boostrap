**Just spun up a production-grade K8s cluster in one command.**

No kidding. This repo automates the entire bootstrap: K3s + ArgoCD GitOps + a full observability stack — all with a single `./scripts/run-all.sh`.

**What's included:**
- PostgreSQL, Redis, RabbitMQ
- Keycloak (OIDC auth)
- Prometheus + Grafana + Loki + OpenTelemetry
- Headlamp dashboard
- Traefik ingress + cert-manager + ExternalDNS

**The Good:**
1. **One-command setup** — Automated credential prompts, secret creation, service deployment
2. **GitOps-native** — ArgoCD App-of-Apps pattern, all manifests in Git
3. **Full observability** — Logs, metrics, and traces out of the box
4. **Secure by default** — kube-score validated, non-root containers, resource limits
5. **OIDC auth** — Keycloak integrates Grafana and ArgoCD

**The Trade-offs:**
1. **Single-node by default** — Great for dev/staging, but you'll need custom scripts for multi-node HA
2. **Linux-only bootstrap scripts** — K3s works elsewhere, but the automation expects Linux
3. **Opinionated stack** — Keycloak, Traefik, Loki — pick your favorites or extend it

**Play with it:**
```
git clone https://github.com/your-repo/k8s-boostrap
cd k8s-boostrap
./scripts/run-all.sh
```

Check the README for access endpoints (ArgoCD, Grafana, Keycloak, Headlamp).

What would you add or remove? Keen to hear how you'd tailor this for your stack.

#Kubernetes #GitOps #ArgoCD #DevOps #K3s #OpenTelemetry