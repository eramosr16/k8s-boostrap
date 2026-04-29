#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/../config.yaml"

get_yaml_value() {
    local key="$1"
    local section="$2"
    local value=""

    if [ -f "$CONFIG_FILE" ]; then
        local in_section=false
        while IFS= read -r line; do
            if [[ "$line" =~ ^${section}: ]]; then
                in_section=true
                continue
            elif [[ "$in_section" && "$line" =~ ^[a-z] ]]; then
                in_section=false
            fi

            if [[ "$in_section" && "$line" =~ ^${key}: ]]; then
                value=$(echo "$line" | sed 's/.*: *//' | tr -d '"')
                break
            fi
        done < "$CONFIG_FILE"
    fi

    echo "$value"
}

get_yaml_list() {
    local key="$1"
    local section="$2"
    local result=""

    if [ -f "$CONFIG_FILE" ]; then
        local in_section=false
        local in_list=false
        while IFS= read -r line; do
            if [[ "$line" =~ ^${section}: ]]; then
                in_section=true
                continue
            elif [[ "$in_section" && "$line" =~ ^[a-z] ]]; then
                in_section=false
            fi

            if [[ "$in_section" ]]; then
                if [[ "$line" =~ ^${key}: ]]; then
                    in_list=true
                    local indent=$(echo "$line" | sed 's/[^ ].*//')
                    continue
                elif [[ "$in_list" && "$line" =~ ^[[:space:]]*- ]]; then
                    local item=$(echo "$line" | sed 's/.*- *//' | tr -d '"')
                    result="${result} ${item}"
                elif [[ "$in_list" && ! "$line" =~ ^[[:space:]] ]]; then
                    in_list=false
                fi
            fi
        done < "$CONFIG_FILE"
    fi

    echo "$result"
}

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

    K3S_EXEC_FLAGS=""

    if [ -f "$CONFIG_FILE" ]; then
        local cluster_domain=$(get_yaml_value "domain" "cluster")
        if [ -n "$cluster_domain" ]; then
            K3S_EXEC_FLAGS="${K3S_EXEC_FLAGS} --cluster-domain=${cluster_domain}"
        fi

        local disable_list=$(get_yaml_list "disable" "k3s")
        if [ -n "$disable_list" ]; then
            for item in $disable_list; do
                K3S_EXEC_FLAGS="${K3S_EXEC_FLAGS} --disable=${item}"
            done
        fi

        local server_flags=$(get_yaml_list "serverFlags" "k3s")
        if [ -n "$server_flags" ]; then
            for flag in $server_flags; do
                K3S_EXEC_FLAGS="${K3S_EXEC_FLAGS} ${flag}"
            done
        fi

        if [ -n "$K3S_EXEC_FLAGS" ]; then
            echo "Applying K3s configuration from config.yaml..."
            echo "K3s exec flags: $K3S_EXEC_FLAGS"
            export INSTALL_K3S_EXEC="server${K3S_EXEC_FLAGS}"
        fi
    fi

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