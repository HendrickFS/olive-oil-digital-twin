# Stopping the Eclipse Ditto docker compose setup
sudo docker compose -f "ditto/deployment/docker/docker-compose.yml" --env-file ".env" stop

# Stopping the database API
cd api
sudo docker compose stop