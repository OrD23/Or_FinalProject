#!/usr/bin/env bash
# wait-for-it.sh

host="$1"
port="$2"
timeout=${3:-30}
shift 3

echo "Waiting for $host:$port (timeout in ${timeout}s)…"

while ! nc -z "$host" "$port"; do
  sleep 1
  timeout=$((timeout - 1))
  if [ "$timeout" -le 0 ]; then
    echo "ERROR: Timeout waiting for $host:$port" >&2
    exit 1
  fi
done

echo "$host:$port is up — proceeding"
exec "$@"
