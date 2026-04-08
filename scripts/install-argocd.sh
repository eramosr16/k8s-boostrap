#!/bin/bash
set -e

echo "=== ArgoCD Installation Script ==="

if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed. Run scripts/bootstrap.sh first."
    exit 1
fi

echo "Creating argocd namespace..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

echo "Installing ArgoCD..."
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "Waiting for ArgoCD to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

echo "Retrieving initial admin password..."
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

echo ""
echo "=== ArgoCD Installation Complete ==="
echo "UI Access: http://localhost:8080"
echo "Username: admin"
echo "Password: ${ARGOCD_PASSWORD}"
echo ""
echo "To access ArgoCD UI, run:"
echo "  kubectl port-forward svc/argocd-server -n argocd 8080:443"