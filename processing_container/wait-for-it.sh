#!/usr/bin/env bash
# wait-for-it.sh

host="$1"
shift
cmd="$@"

until nc -z "$host" 1883; do
  echo "Waiting for the service $host:1883..."
  sleep 1
done

exec $cmd