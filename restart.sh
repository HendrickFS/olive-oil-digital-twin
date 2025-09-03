# Running the Eclipse Ditto docker compose setup
sudo docker compose -f "ditto/deployment/docker/docker-compose.yml" --env-file ".env" up -d --wait

# Accessing the InfluxDB connection utility
cd utils
cd influxdb_connection

# Setting up the InfluxDB connection
mvn install
nohup mvn spring-boot:run > logs.txt 2>&1 &


cd ../..
cd api

# Starting API services for database
sudo docker compose up -d
