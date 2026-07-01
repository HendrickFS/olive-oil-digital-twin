# Olive Oil Digital Twin 🫒

A modern, containerized IoT Digital Twin framework designed for real-time monitoring, data ingestion, and predictive quality analysis in olive oil production facilities.

---

## 📋 Project Overview

This repository implements a virtual representation (Digital Twin) of an industrial olive oil extraction plant. It tracks and synchronizes the state of physical shop-floor machinery—including deposits (storage tanks), mills, mixers (malaxators), centrifuges, decanters, and hoppers—translating sensor telemetry into real-time digital states and predicting final olive oil quality.

### Key Highlights
*   🤖 **State-of-the-Art Digital Twins**: Powered by **Eclipse Ditto** to maintain device properties, lifecycle policies, and digital-to-physical sync.
*   📡 **MQTT Event Ingestion**: Real-time sensor mapping through **Eclipse Mosquitto** using custom JavaScript payload converters.
*   🧠 **Predictive Quality Analysis**: Integrates **CatBoost multi-target regression** to predict 10 continuous quality variables (such as acidity, yield, and phenols) and assess **International Olive Council (IOC)** compliance.
*   📊 **Time-Series Logging**: Automatic persistence of device telemetry into **InfluxDB** for historical analysis.
*   🔌 **Developer Interface**: A lightweight **Flask API** wrapper enabling downstream web applications or dashboards to query live state, historical logs, and ML diagnostics.

---

## 🏗️ System Architecture

The following diagram illustrates the structural layout of the Digital Twin Framework, mapping the data flow from physical equipment and edge sensors up to the core management services and visual interfaces.

![Digital Twin Framework Architecture](docs/dt_architecture_v8(1).png)

*For an in-depth breakdown of each architectural layer, sub-entity, and the observable physical elements, see the [Architecture Documentation](docs/architecture.md).*

---

## 📁 Repository Documentation Directory

The documentation is organized into modular guides within the `docs/` folder:

| Document | Description |
| :--- | :--- |
| 🏗️ **[System Architecture](docs/architecture.md)** | Explains the structural entities (User, Core, Edge, Physical Assets) shown in the architecture diagram. |
| ⚙️ **[Setup & Usage Guide](docs/setup_and_usage.md)** | Step-by-step commands to launch containers, run simulations, query API endpoints, and troubleshoot environment setups. |
| 🧠 **[Machine Learning Integration](docs/machine_learning.md)** | In-depth breakdown of ML model choices, empirical benchmarks (CatBoost vs. XGBoost vs. RF), and performance graphics. |

---

## 🚀 Quick Start

To spin up the local development stack and verify the digital twin system, follow these steps:

### 1. Launch the Service Stack
Ensure you have **Docker Desktop** running, then execute:
```bash
./run.sh
```
*This starts the Eclipse Ditto core, Mosquitto MQTT broker, InfluxDB database, and the Flask API backend on a shared virtual bridge network (`mqtt-shared`).*

### 2. Configure System Resources
Provision Ditto with default device models, access control list (ACL) policies, and MQTT topics mapping configurations:
```bash
cd scripts
python config.py
```

### 3. Access Interfaces
Once running, you can interact with the system via these web panels:
*   **Eclipse Ditto UI**: [http://localhost:8080](http://localhost:8080) (Credentials: `ditto` / `ditto`)
*   **InfluxDB UI**: [http://localhost:9999](http://localhost:9999) (Credentials: `admin` / `admin123`)
*   **Flask API Gateway**: [http://localhost:5555/health](http://localhost:5555/health)

---

## 📂 Project Structure

```
digitalTwin/
├── api/                   # REST API application and Docker orchestration
│   ├── app.py             # Main Flask application with /data and /ml endpoints
│   └── requirements.txt   # API service requirements
├── connections/           # Ditto connection schemas with embedded JS payload mappers
├── docs/                  # System documentation and diagram assets
│   ├── architecture.md    # Detail view of system architecture
│   ├── machine_learning.md# Details of the CatBoost multi-target regression pipeline
│   └── setup_and_usage.md # Setup guide and API reference
├── ditto/                 # Eclipse Ditto container configurations and orchestration
├── ml/                    # Machine learning models, training scripts, and comparison benchmarks
│   ├── datasets/          # Synthetic training datasets (1K and 3K records)
│   ├── images/            # Actual-vs-predicted plots and validation charts
│   ├── train_catboost.py  # Model training script
│   └── requirements-ml.txt# ML dependencies
├── policies/              # JSON authorization policies for the digital twins
├── models/                # JSON schemas defining the Digital Twin properties per device
└── scripts/               # Simulator tools and automated environment config scripts
```

---

## 🤝 Acknowledgements

*   **Eclipse Ditto** for the open-source Digital Twin platform framework.
*   **InfluxDB** for the high-performance time-series database.
*   **Eclipse Mosquitto** for the lightweight message broker.
*   **SustainOlive** project for domain expertise and operational requirements.
