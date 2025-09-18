# Stopping the Eclipse Ditto docker compose setup
sudo docker compose -f "ditto/deployment/docker/docker-compose.yml" --env-file ".influx_env" stop

# Stopping the database API
cd api
sudo docker compose stop