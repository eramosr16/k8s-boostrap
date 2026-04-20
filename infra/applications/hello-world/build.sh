#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FUNC_NAME="${FUNC_NAME:-nuclio-hello-world}"
REGISTRY="${REGISTRY:-localhost:5000}"
NAMESPACE="${NAMESPACE:-default}"

NUCTL_IMAGE="nuclio-cli:latest"

build_nuctl_image() {
    echo "Building nuctl CLI image..."
    cat > /tmp/Dockerfile.nuctl << 'EOF'
FROM alpine:3.18
RUN apk add --no-cache curl tar
ARG NUCTL_VERSION=1.12.0
RUN curl -sL "https://github.com/nuclio/nuclio/releases/download/${NUCTL_VERSION}/nuctl-${NUCTL_VERSION}-linux-amd64" -o /usr/local/bin/nuctl && \
    chmod +x /usr/local/bin/nuctl
ENTRYPOINT ["nuctl"]
EOF
    docker build -t "$NUCTL_IMAGE" -f /tmp/Dockerfile.nuctl /tmp
}

run_nuctl() {
    docker run --rm -it \
        --network host \
        -v "$SCRIPT_DIR:/func" \
        -v "$HOME/.kube:/kubeconfig:ro" \
        -e KUBECONFIG=/kubeconfig \
        "$NUCTL_IMAGE" "$@"
}

check_nuctl() {
    if ! docker image inspect "$NUCTL_IMAGE" > /dev/null 2>&1; then
        build_nuctl_image
    fi
}

check_nuctl

echo "Building function: $FUNC_NAME"

docker build -t "${REGISTRY}/${FUNC_NAME}:local" "$SCRIPT_DIR"

echo "Build complete: ${REGISTRY}/${FUNC_NAME}:local"