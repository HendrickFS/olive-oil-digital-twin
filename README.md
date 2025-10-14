# Olive Oil Digital Twin 🫒

A comprehensive digital twin system for monitoring and managing olive oil production processes using IoT sensors and modern containerized architecture.

## 📋 Overview

This project creates a digital representation of olive oil production equipment including deposits, mills, mixers, centrifuges, decanters, and bins. The system collects real-time sensor data, stores it for analysis, and provides APIs for data access and visualization.

### Key Components
- **Eclipse Ditto**: Digital twin platform for device management
- **InfluxDB**: Time-series database for sensor data storage
- **MQTT**: Message broker for real-time data communication
- **Flask API**: RESTful API for data access
- **Docker**: Containerized deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   IoT Sensors   │───▶│   MQTT Broker   │───▶│  Eclipse Ditto  │
│ (Temperature,   │    │   (Mosquitto)   │    │ (Digital Twins) │
│  Humidity, MQ)  │    └─────────────────┘    └─────────────────┘
└─────────────────┘                                      │
                                                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask API     │◀───│    InfluxDB     │◀───│   Data Flow     │
│ (Port 5555)     │    │  (Time Series)  │    │   Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Getting Started

### Prerequisites
- Docker Desktop
- Python 3.11+
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/HendrickFS/olive-oil-digital-twin.git
   cd olive-oil-digital-twin
   ```

2. **Start the system**
   ```bash
   ./run.sh
   ```
   
   Or on Windows PowerShell:
   ```powershell
   bash run.sh
   ```

3. **Access the services**
   - **Ditto UI**: http://localhost:8080
   - **InfluxDB**: http://localhost:9999
   - **API**: http://localhost:5555
   - **MQTT**: localhost:1884

## 📦 Services

### Eclipse Ditto (Digital Twin Platform)
- **Port**: 8081 (Gateway), 8080 (UI)
- **Authentication**: `ditto:ditto`
- **Purpose**: Manages digital twins of production equipment

### InfluxDB (Time Series Database)
- **Port**: 9999
- **UI**: http://localhost:9999
- **Credentials**: `admin:admin123`
- **Organization**: SustainOlive
- **Bucket**: DigitalTwin

### MQTT Broker (Mosquitto)
- **Port**: 1884
- **Purpose**: Real-time sensor data communication

### Flask API
- **Port**: 5555
- **Endpoints**:
  - `GET /data?thingId=<id>&feature=<feature>&range_start=<time>`
  - `GET /health` - Health check

## 🔧 Configuration

### Environment Variables
The system uses `.influx_env` file for InfluxDB configuration:
```bash
DOCKER_INFLUXDB_INIT_MODE=setup
DOCKER_INFLUXDB_INIT_USERNAME=admin
DOCKER_INFLUXDB_INIT_PASSWORD=admin123
DOCKER_INFLUXDB_INIT_ORG=SustainOlive
DOCKER_INFLUXDB_INIT_BUCKET=DigitalTwin
DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=<your-token>
```

### Digital Twin Models
The system manages the following equipment types:
- **Deposits** (3 units): Temperature, humidity, MQ sensors
- **Mills** (1 unit): Production monitoring
- **Mixers** (2 units): Mixing process control
- **Centrifuges** (1 unit): Separation monitoring
- **Decanters** (1 unit): Final separation
- **Bins** (1 unit): Storage monitoring

## 🛠️ Development

### Project Structure
```
digitalTwin/
├── api/                    # Flask API application
│   ├── app.py             # Main API application
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Container configuration
│   └── docker-compose.yml # API service setup
├── ditto/                 # Eclipse Ditto configuration
│   └── deployment/docker/ # Docker compose for Ditto
├── connections/           # MQTT connection configs
├── models/                # Digital twin models (JSON)
├── policies/              # Access control policies
├── scripts/               # Setup and test scripts
│   ├── config.py         # System configuration
│   └── test_connection.py # MQTT sensor simulation
├── utils/                 # Utility applications
│   └── influxdb_connection/ # InfluxDB integration
├── .influx_env           # InfluxDB environment variables
└── run.sh                # Main startup script
```

### Running Individual Components

#### API Development
```bash
cd api
pip install -r requirements.txt
python app.py  # Development mode
# or
gunicorn --bind 0.0.0.0:5555 --workers 2 app:app  # Production mode
```

#### Sensor Simulation
```bash
cd scripts
python test_connection.py
```

#### System Configuration
```bash
cd scripts
python config.py
```

### API Usage Examples

**Get temperature data for deposit001**
```bash
curl "http://localhost:5555/data?thingId=olive.production:deposit001&feature=temperature&range_start=-1h"
```

**Get humidity data for the last 24 hours**
```bash
curl "http://localhost:5555/data?thingId=olive.production:deposit002&feature=humidity&range_start=-24h"
```

**Health check**
```bash
curl "http://localhost:5555/health"
```

## 📊 Monitoring

### Health Checks
- **InfluxDB**: http://localhost:9999/health
- **API**: http://localhost:5555/health
- **Ditto Gateway**: http://localhost:8081/status/health

### Container Status
```bash
# Check all containers
docker-compose ps

# View logs
docker-compose logs -f influxdb
docker-compose logs -f ditto-gateway
```

## 🔄 Data Flow

1. **Sensor Data Collection**: IoT sensors collect temperature, humidity, and MQ readings from production equipment
2. **MQTT Publishing**: Sensor data is published to MQTT topics (`deposit/incoming/{deviceId}`)
3. **Ditto Processing**: Eclipse Ditto receives MQTT messages and updates digital twin states
4. **InfluxDB Storage**: Processed data is stored in InfluxDB time-series database for historical analysis
5. **API Access**: Flask API provides HTTP endpoints for querying stored sensor data
6. **Visualization**: External applications can consume API data for real-time dashboards and analytics

## 🛡️ Security

- **Authentication**: Basic authentication for Ditto (`ditto:ditto`) and InfluxDB (`admin:admin123`)
- **Network Isolation**: Services communicate through isolated Docker networks
- **Environment Variables**: Sensitive configuration stored in `.influx_env` file
- **CORS**: API configured with Cross-Origin Resource Sharing for web applications

## 🚨 Troubleshooting

### Common Issues

**InfluxDB won't start**
- Check if port 9999 is available: `netstat -an | findstr 9999`
- Verify environment variables in `.influx_env` file
- Check Docker logs: `docker-compose logs influxdb`
- Ensure Docker has enough memory allocated

**MQTT Connection Failed**
- Ensure Mosquitto is running on port 1884
- Check network connectivity: `docker network ls`
- Verify MQTT broker configuration in `mosquitto.conf`

**API Returns Empty Data**
- Verify InfluxDB connection and data exists
- Check if sensor simulation is running: `python scripts/test_connection.py`
- Validate query parameters (thingId, feature, range_start)
- Check API logs for connection errors

**Ditto Services Unhealthy**
- Check MongoDB connection (Ditto's database)
- Verify all service dependencies are running
- Review container resource limits and memory usage
- Check Ditto gateway logs for authentication issues

**Docker Compose Issues**
- Ensure Docker Desktop is running
- Check for port conflicts with existing services
- Verify all required environment files exist
- Try rebuilding containers: `docker-compose up --build`

### Useful Commands
```bash
# Restart all services
docker-compose restart

# Rebuild and start containers
docker-compose up --build

# View real-time logs
docker-compose logs -f

# Stop all services
docker-compose down

# Clean up volumes and networks
docker-compose down -v

# Check container resource usage
docker stats
```

## 🔧 Configuration Files

### Key Configuration Files
- **`.influx_env`**: InfluxDB initialization settings
- **`docker-compose.yml`**: Main service orchestration
- **`mosquitto.conf`**: MQTT broker configuration
- **`models/*.json`**: Digital twin device definitions
- **`policies/*.json`**: Access control policies
- **`connections/*.json`**: MQTT connection configurations

### Customization
To customize the system for your environment:

1. **Update ports** in `docker-compose.yml` if conflicts exist
2. **Modify sensor data** in `scripts/test_connection.py`
3. **Add new device models** in `models/` directory
4. **Configure API endpoints** in `api/app.py`
5. **Adjust InfluxDB settings** in `.influx_env`

## 📈 Future Enhancements

- [X] Web dashboard for real-time monitoring and visualization
- [ ] Machine learning algorithms for predictive maintenance
- [ ] Advanced alerting system with email notifications
- [ ] Historical data analytics and reporting
- [ ] Advanced security with OAuth2/JWT authentication


## 🙏 Acknowledgments

- **Eclipse Ditto** team for the excellent digital twin platform
- **InfluxDB** for robust time-series database capabilities  
- **Eclipse Mosquitto** for reliable MQTT messaging
- **Flask** community for the lightweight web framework
- **SustainOlive** project for the domain expertise and requirements
