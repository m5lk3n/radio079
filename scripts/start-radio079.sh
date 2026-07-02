#!/bin/sh

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VERSION=$(git describe --tags --always --dirty | sed 's/^v//')

docker run -d \
  --restart unless-stopped \
  --env-file ${BASE_DIR}/.env \
  -v ${BASE_DIR}/data:/app/data \
  -v ${BASE_DIR}/jingles:/app/jingles \
  -p 127.0.0.1:8079:8079 \
  -e PUID=$(id -u) \
  -e PGID=$(id -g) \
  --name radio079 \
  lttl.dev/radio079:${VERSION} --webserver