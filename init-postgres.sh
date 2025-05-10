#!/bin/bash
set -e

PGPASSWORD=$POSTGRESQL_PASSWORD psql -v ON_ERROR_STOP=1 --username "$POSTGRESQL_USERNAME" --dbname "postgres" <<-EOSQL
    CREATE DATABASE systemdb;
EOSQL