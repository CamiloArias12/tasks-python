#!/bin/sh

if [ -n "$1" ]; then
    ENV="$1"
else
    if [ -f .env ]; then
        . ./.env
        if [ -z "${ENV:-}" ]; then
            echo "ENV no está definido en .env y no se pasó como parámetro."
            echo "Uso: $0 <ENV> (o define ENV en .env)"
            exit 1
        fi
    else
        echo ".env no encontrado y no se pasó parámetro."
        echo "Uso: $0 <ENV> (o crea .env con ENV=...)"
        exit 1
    fi
fi

docker-compose -f compose.${ENV}.yml down
git pull
docker-compose -f compose.${ENV}.yml up -d --build