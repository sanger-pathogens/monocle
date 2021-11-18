#!/usr/bin/env bash

MONOCLE_HOST=$1
API_BASE_ROUTE="/metadata"
OPENAPI_SCHEMA="metadata/interface/openapi.yml"

if [ -z ${MONOCLE_HOST} ]
then
  echo "Usage: ${0} hostname"
  echo "Specify the host name (or floating IP address) for the Monocle API you want to test"
  exit 1
fi

schemathesis run  --base-url "http://${MONOCLE_HOST}${API_BASE_ROUTE}" \
                  --validate-schema=false \
                  "${OPENAPI_SCHEMA}"
