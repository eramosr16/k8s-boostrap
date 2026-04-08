#!/bin/bash
set -e

echo "=== K3s Bootstrap Script ==="

if command -v k3s &> /dev/null; then
    echo "K3s is already installed: $(k3s --version)"
    echo "Checking K3s service status..."
    if systemctl is-active --quiet k3s; then
        echo "K3s service is running."
    else
        echo "K3s is installed but not running. Starting service..."
        sudo systemctl start k3s
    fi
else
    echo "K3s not found. Installing K3s..."
    curl -sfL https://get.k3s.io | sh -
    echo "K3s installed successfully."
fi

echo "Setting up kubectl configuration..."
K3S_KUBECONFIG="/etc/rancher/k3s/k3s.yaml"
KUBECONFIG_DIR="${HOME}/.kube"
KUBECONFIG_FILE="${KUBECONFIG_DIR}/config"

mkdir -p "${KUBECONFIG_DIR}"

if [ -f "${K3S_KUBECONFIG}" ]; then
    if [ ! -f "${KUBECONFIG_FILE}" ] || ! diff -q "${K3S_KUBECONFIG}" "${KUBECONFIG_FILE}" &> /dev/null; then
        sudo cp "${K3S_KUBECONFIG}" "${KUBECONFIG_FILE}"
        sudo chmod 600 "${KUBECONFIG_FILE}"
        echo "Kubeconfig copied to ${KUBECONFIG_FILE}"
    else
        echo "Kubeconfig already configured."
    fi
else
    echo "Warning: K3s kubeconfig not found at ${K3S_KUBECONFIG}"
fi

echo "Verifying cluster connectivity..."
kubectl cluster-info

echo "=== K3s Bootstrap Complete ==="
echo "Run 'kubectl get nodes' to see cluster status."