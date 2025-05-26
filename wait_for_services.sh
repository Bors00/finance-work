#!/bin/bash
function wait_for() {
    local host=$1
    local port=$2
    echo "Attente de $host sur le port $port..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$host:$port est accessible."
}

# Attendre que PostgreSQL soit accessible
wait_for db 5432
