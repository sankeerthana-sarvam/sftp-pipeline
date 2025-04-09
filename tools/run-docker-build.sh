#!/bin/bash
export DOCKER_BUILDKIT=1
# shellcheck disable=SC2164
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd $ROOT_DIR

docker build  \
    --secret=id=creds,src="${HOME}/.config/gcloud/application_default_credentials.json" \
    -f tools/Dockerfile.CronJob \
    -t cookiecutter-py-service:latest \
    .
