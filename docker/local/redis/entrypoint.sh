#!/bin/sh
set -e

# OVERRIDE the official /usr/local/bin/docker-entrypoint.sh

REDIS_PASSWORD="$(cat $REDIS_PASSWORD_FILE)"
set -- "$@" --requirepass $REDIS_PASSWORD

# set an appropriate umask (if one isn't set already)
# - https://github.com/docker-library/redis/issues/305
# - https://github.com/redis/redis/blob/bb875603fb7ff3f9d19aad906bd45d7db98d9a39/utils/systemd-redis_server.service#L37
umask 0077

exec "$@"
