helm upgrade --install nuclio nuclio/nuclio \
  --namespace services \
  --version 0.21.24 \
  --set dashboard.containerBuilderKind=kaniko \
  --set dashboard.kaniko.registryProviderSecretName=aws-credentials \
  --set registry.secretName=ecr-registry-secret \
  --set registry.pushPullUrl=701338182393.dkr.ecr.us-east-1.amazonaws.com/nuclio/functions \
  --set dashboard.kaniko.cacheRepo=701338182393.dkr.ecr.us-east-1.amazonaws.com/nuclio/cache \
  --set controller.image.tag=latest-amd64 \
  --set dashboard.image.tag=latest-amd64
