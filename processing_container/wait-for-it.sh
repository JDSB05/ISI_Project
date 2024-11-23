#!/usr/bin/env bash
# wait-for-it.sh

set -e

host="$1"
shift
cmd="$@"

until nc -z "$host" 1883; do
  >&2 echo "MQTT broker is unavailable - sleeping"
  sleep 1
done

>&2 echo "MQTT broker is up - executing command"
exec $cmd