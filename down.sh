#!/bin/bash

sudo docker compose -f "ditto/deployment/docker/docker-compose.yml" --env-file ".influx_env" down