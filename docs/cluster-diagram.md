# Cluster Architecture Diagram

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e3f2fd', 'primaryTextColor': '#1565c0', 'primaryBorderColor': '#1976d2', 'lineColor': '#616161', 'secondaryColor': '#f3e5f5', 'tertiaryColor': '#fff3e0'}}}%%
flowchart TB
    subgraph K3s["K3s Cluster"]
        subgraph infra_ns["infra"]
            subgraph dbs["Databases"]
                PG["PostgreSQL<br/>:5432"]
                RD["Redis<br/>:6379"]
            end
            
            subgraph mq["Message Broker"]
                RMQ["RabbitMQ<br/>:5672"]
            end
            
            subgraph iam["IAM"]
                KC["Keycloak<br/>:8080"]
            end
            
            subgraph obs["Observability"]
                PRO["Prometheus<br/>:9090"]
                GRAF["Grafana<br/>:3000"]
                LOKI["Loki<br/>:3100"]
                OTEL["Otel Collector<br/>:4317"]
                HEAD["Headlamp<br/>:80"]
                ARGO["ArgoCD<br/>:443"]
            end
            
            subgraph gw["Gateway"]
                TRF["Traefik<br/>Ingress"]
            end
            
            subgraph reg["Registry"]
                ECR["ECR Provider"]
            end
        end
        
        subgraph apps_ns["applications"]
            HW["hello-world<br/>:8080"]
        end
    end
    
    EXT["External<br/>Users"] --> TRF
    TRF --> KC
    TRF --> GRAF
    TRF --> ARGO
    TRF --> LOKI
    TRF --> HEAD
    TRF --> HW
    
    KC --> PG
    KC --> RD
    
    GRAF --> PRO
    
    OTEL --> PRO
    OTEL --> LOKI
    
    HW --> PG
    HW --> RD
    HW --> RMQ
    
    classDef db fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    classDef broker fill:#fff3e0,stroke:#ef6c00,color:#e65100
    classDef iam fill:#e1f5fe,stroke:#0277bd,color:#01579b
    classDef obs fill:#fce4ec,stroke:#c2185b,color:#880e4f
    classDef gw fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c
    classDef reg fill:#efebe9,stroke:#5d4037,color:#3e2723
    classDef app fill:#e0f7fa,stroke:#00838f,color:#006064
    classDef user fill:#424242,stroke:#212121,color:#ffffff
    
    class PG,RD db
    class RMQ broker
    class KC iam
    class PRO,GRAF,LOKI,OTEL,HEAD,ARGO obs
    class TRF gw
    class ECR reg
    class HW app
    class EXT user
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
| | Loki | 3100 | ClusterIP | Log aggregation |
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
5. **Observability** (Prometheus, Grafana, Loki, OpenTelemetry, Headlamp, ArgoCD)
6. **Registry** (ECR Credential Provider)
7. **Applications** (hello-world)