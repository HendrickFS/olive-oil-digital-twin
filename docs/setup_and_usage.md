# Setup and Usage Guide

This guide provides detailed instructions on how to set up, run, configure, and troubleshoot the **Olive Oil Digital Twin** system.

---

## 📋 System Prerequisites

Before starting, ensure your host machine has the following tools installed:
*   **Docker Desktop** (with Compose version 2+)
*   **Python 3.11+**
*   **Maven 3.8+ & Java JDK 17** (optional, only if rebuilding the InfluxDB connection adapter manually)
*   **Git**

---

## 🏗️ Services Overview

The digital twin network orchestrates multiple containerized and local services:

| Service | Port | Default Credentials | Description / Purpose |
| :--- | :---: | :--- | :--- |
| **Eclipse Ditto Gateway** | `8081` | `ditto:ditto` | REST API gateway for managing digital twin assets. |
| **Eclipse Ditto UI** | `8080` | `ditto:ditto` | Web-based explorer for Twin states and policies. |
| **InfluxDB** | `9999` | `admin:admin123` | Time-series database storing sensor data logs. |
| **MQTT Broker** | `1884` | `sustainolive:sustainolive` | Mosquitto broker handling telemetry ingestion topics. |
| **Flask API** | `5555` | None | REST API interfacing database queries for client applications. |

---

## 🚀 Getting Started

### 1. Launching the Container Stack
Start the MQTT broker, InfluxDB, and Eclipse Ditto by executing the main shell script:
```bash
./run.sh
```
Or on Windows:
```powershell
bash run.sh
```
*This command creates a shared Docker bridge network (`mqtt-shared`) if it doesn't already exist and spins up all infrastructure services.*

### 2. Initial Setup Script
The initialization script publishes required twin models, default access control policies, and connection configurations to Eclipse Ditto:
```bash
cd scripts
python config.py
```
*This runs the following sequential operations:*
1.  **Upload Policy** (`upload_policy.py`): Posts `policies/defaultPolicy.json` to Ditto.
2.  **Create Twins** (`create_twins.py`): Instantiates digital twin states in Ditto matching the definitions in `models/*.json`.
3.  **Upload Connections** (`upload_connection.py`): Configures Ditto to listen to MQTT topics under `batch/incoming/#`.

### 3. Simulating Sensor Telemetry
To simulate continuous live sensor inputs (temperature, moisture, oil content) from olive mill production elements, run the MQTT test simulation:
```bash
cd scripts
python test_connection.py
```

---

## 🔌 API Endpoints & Usage

The Flask API runs on port `5555` and bridges client requests with historical database queries.

### A. Get Historical Sensor Data
Retrieve records for a specific physical thing, feature, and time range.
*   **URL**: `/data`
*   **Method**: `GET`
*   **Parameters**:
    *   `thingId` (string, required): The Ditto identifier (e.g. `olive.production:deposit001`).
    *   `feature` (string, required): The target property (e.g. `temperature`, `humidity`).
    *   `range_start` (string, optional): Time-series range (default `-24h`, supports `-1h`, `-30d`).
    *   `dedup` (boolean, optional): Set to `true` to deduplicate identical timestamps.
    *   `latest` (boolean, optional): Set to `true` to return only the single newest record.

**Example Request**:
```bash
curl "http://localhost:5555/data?thingId=olive.production:deposit001&feature=temperature&range_start=-2h"
```

### B. Machine Learning Anomaly Detection
Analyze sensor history using the Isolation Forest algorithm to flags anomalies.
*   **URL**: `/ml/anomaly`
*   **Method**: `GET`
*   **Parameters**:
    *   `thingId` (string, required): Target digital twin ID.
    *   `feature` (string, required): Telemetry feature to analyze.
    *   `training_range` (string, optional): History to train on (default `-24h`).
    *   `range_start` (string, optional): Window to evaluate (default `-1h`).

**Example Request**:
```bash
curl "http://localhost:5555/ml/anomaly?thingId=olive.production:deposit001&feature=temperature"
```

---

## 🚨 Troubleshooting

### InfluxDB Connection Issues
*   Verify that InfluxDB is running at `http://localhost:9999`.
*   Ensure the `.influx_env` configuration matches your container setup:
    ```env
    DOCKER_INFLUXDB_INIT_USERNAME=admin
    DOCKER_INFLUXDB_INIT_PASSWORD=admin123
    DOCKER_INFLUXDB_INIT_ORG=SustainOlive
    DOCKER_INFLUXDB_INIT_BUCKET=DigitalTwin
    ```
*   If InfluxDB fails to mount, inspect container resource limits in Docker Desktop.

### Eclipse Ditto Services Unhealthy
*   Ditto requires a backend MongoDB container. Check logs:
    ```bash
    docker compose -f ditto/deployment/docker/docker-compose.yml logs -f ditto-gateway
    ```
*   If ports conflict, check what is using port `8080` (commonly web servers or development tools):
    ```bash
    netstat -ano | findstr 8080
    ```

### MQTT Payload Issues (Ditto Mapper)
*   Eclipse Ditto maps raw MQTT bytes to internal twin models using the JavaScript mapping scripts under `connections/*.json`.
*   If payload updates aren't reflecting, check Mosquitto broker logs:
    ```bash
    docker compose -f ditto/deployment/docker/docker-compose.yml logs -f mosquitto
    ```
*   You can verify payload publishes manually using `mosquitto_sub` or a tool like MQTT Explorer.
