# Cluster Architecture Diagram

```mermaid
flowchart TB
    subgraph K3s_Cluster["K3s Cluster"]
        subgraph infra["infra Namespace"]
            subgraph Databases["Databases"]
                PostgreSQL["PostgreSQL<br/>:5432"]
                Redis["Redis<br/>:6379"]
            end
            
            subgraph Broker["Message Broker"]
                RabbitMQ["RabbitMQ<br/>:5672<br/>:15672"]
            end
            
            subgraph IAM["Identity & Access"]
                Keycloak["Keycloak<br/>:8080"]
            end
            
            subgraph Observability["Observability"]
                Prometheus["Prometheus<br/>:9090"]
                Grafana["Grafana<br/>:3000"]
                Seq["Seq<br/>:5341"]
                OpenTelemetry["OpenTelemetry<br/>:4317"]
                Headlamp["Headlamp<br/>:80"]
                ArgoCD["ArgoCD<br/>:443"]
            end
            
            subgraph Gateway["Gateway"]
                Traefik["Traefik<br/>Ingress Controller"]
                CertManager["Cert Manager"]
                ExternalDNS["External DNS"]
            end
            
            subgraph Registry["Registry"]
                ECR["ECR Credential<br/>Provider"]
            end
        end
        
        subgraph applications["applications Namespace"]
            HelloWorld["hello-world<br/>:8080"]
        end
    end
    
    External["External Users"] --> Traefik
    Traefik --> Keycloak
    Traefik --> Grafana
    Traefik --> ArgoCD
    Traefik --> Seq
    Traefik --> Headlamp
    Traefik --> HelloWorld
    
    Keycloak --> PostgreSQL
    Keycloak --> Redis
    
    Grafana --> Prometheus
    Grafana --> PostgreSQL
    
    OpenTelemetry --> Prometheus
    OpenTelemetry --> Seq
    
    hello-world["hello-world app"] --> PostgreSQL
    hello-world --> Redis
    hello-world --> RabbitMQ
```

## Service Overview

| Category | Service | Port | Type | Purpose |
| -------- | -------- | ---- | ---- | ------- |
| **Databases** | PostgreSQL | 5432 | ClusterIP | Primary database |
| | Redis | 6379 | ClusterIP | Cache store |
| **Broker** | RabbitMQ | 5672/15672 | ClusterIP | Message broker |
| **IAM** | Keycloak | 8080 | ClusterID | Identity provider |
| **Observability** | Prometheus | 9090 | ClusterIP | Metrics |
| | Grafana | 3000 | ClusterIP | Visualization |
| | Seq | 5341 | ClusterIP | Log aggregation |
| | OpenTelemetry | 4317 | ClusterIP |Tracing |
| | Headlamp | 80 | ClusterIP | K8s UI |
| | ArgoCD | 443 | ClusterIP | GitOps |
| **Gateway** | Traefik | 80/443 | LoadBalancer | Ingress |
| **Registry** | ECR Provider | - | DaemonSet | AWS ECR auth |

## Deployment Order

1. **Databases** (PostgreSQL, Redis)
2. **Broker** (RabbitMQ)
3. **Gateway** (Traefik)
4. **IAM** (Keycloak)
5. **Observability** (Prometheus, Grafana, Seq, OpenTelemetry, Headlamp, ArgoCD)
6. **Registry** (ECR Credential Provider)
7. **Applications** (hello-world)