#!/bin/bash

NETWORK_NAME="mqtt-shared"

if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  echo "Criando rede: $NETWORK_NAME"
  sudo docker network create "$NETWORK_NAME"
else
  echo "Rede $NETWORK_NAME já existe."
fi

# Running the Eclipse Ditto docker compose setup
sudo docker compose -f "ditto/deployment/docker/docker-compose.yml" --env-file ".env" up -d --wait

# Accessing the InfluxDB connection utility
cd utils
cd influxdb_connection

# Setting up the InfluxDB connection
mvn install
nohup mvn spring-boot:run > logs.txt 2>&1 &

# Accessing the config scripts
cd ../..
cd scripts

# Running starting config script
python3 config.py

# Accessing the database API
cd ..
cd api

# Starting API services for database
sudo docker compose up -d
