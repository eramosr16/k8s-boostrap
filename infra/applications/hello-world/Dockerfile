ARG NUCLIO_LABEL=0.5.6
ARG NUCLIO_ARCH=amd64
ARG NUCLIO_BASE_IMAGE=mcr.microsoft.com/dotnet/sdk:7.0
ARG NUCLIO_ONBUILD_IMAGE=nuclio/handler-builder-dotnetcore-onbuild:${NUCLIO_LABEL}-${NUCLIO_ARCH}

FROM gcr.io/iguazio/uhttpc:0.0.3-amd64 as uhttpc

FROM ${NUCLIO_ONBUILD_IMAGE} as builder

FROM ${NUCLIO_BASE_IMAGE}

COPY --from=builder /home/nuclio/bin/processor /usr/local/bin/processor
COPY --from=builder /home/nuclio/bin/wrapper /opt/nuclio/wrapper
COPY --from=builder /home/nuclio/bin/handler /opt/nuclio/handler
COPY --from=builder /home/nuclio/src/nuclio-sdk-dotnetcore /opt/nuclio/nuclio-sdk-dotnetcore
COPY --from=uhttpc /home/nuclio/bin/uhttpc /usr/local/bin/uhttpc

HEALTHCHECK --interval=1s --timeout=3s CMD /usr/local/bin/uhttpc --url http://127.0.0.1:8082/ready || exit 1

CMD [ "processor" ]