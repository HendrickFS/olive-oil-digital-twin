# Anomaly Detection Implementation Plan

## Goal Description
Implement an AI-based anomaly detection system for the Olive Oil Digital Twin. The system will use the Isolation Forest algorithm to detect anomalies in sensor data (temperature, humidity, etc.) from various devices. A reference frontend dashboard will be created to visualize these anomalies.

## User Review Required
> [!IMPORTANT]
> - New dependencies `scikit-learn` and `pandas` will be added to `api/requirements.txt`.
> - A new directory `dashboard` will be created for the frontend reference implementation.
> - The anomaly detection is "unsupervised" and assumes that the majority of historical data represents "normal" behavior.

## Proposed Changes

### API Layer
#### [MODIFY] [requirements.txt](api/requirements.txt)
- Add `scikit-learn`
- Add `pandas`
- Add `numpy`

#### [MODIFY] [anomaly_detection.py](api/ml/anomaly_detection.py)
- Implement `AnomalyDetector` class.
- Use `sklearn.ensemble.IsolationForest`.
- Add methods for training (fitting) and prediction.
- Implement simple model caching (in-memory) to avoid retraining on every request.

#### [MODIFY] [app.py](api/app.py)
- Update `/ml/anomaly` endpoint.
- Logic:
    1. Fetch historical data (e.g., last 24h) from InfluxDB.
    2. Train/Fit Isolation Forest model on this data.
    3. Detect anomalies in the requested range.
    4. Return JSON with anomaly flags and scores.

### Frontend (New)
#### [NEW] [dashboard/index.html](dashboard/index.html)
- **Framework**: Single Page Application (SPA) using HTML5, CSS3, and Vanilla JS.
- **Visualization Library**: `Chart.js` (via CDN) for responsive and interactive charts.
- **Components**:
    1.  **Control Panel**: Dropdowns for Device (ThingId), Feature (Temperature, etc.), and Time Range.
    2.  **Summary Cards**:
        -   Current Status (Normal/Critical)
        -   Total Anomalies (Last 24h)
        -   Min/Max/Avg Values
    3.  **Main Chart**:
        -   Line chart showing sensor data over time.
        -   **Visual Anomaly Indicators**: Anomalous data points plotted as distinct red points on top of the blue trend line.
        -   Hover tooltips showing exact value and timestamp.
    4.  **Anomaly Log**: A data table listing detected anomalies with timestamps and values for quick reference.
- **Design**: Modern, clean interface using CSS Grid/Flexbox.


## Verification Plan

### Automated Tests
- Run `api/app.py` locally and use `curl` to hit `/ml/anomaly` endpoint.
- Verify JSON response contains `anomaly_detected` boolean and `anomalies` list.

### Manual Verification
1. Start the API: `cd api && python app.py`.
2. Open `dashboard/index.html` in a browser.
3. Select a device (e.g., `deposit001`) and feature (e.g., `temperature`).
4. Click "Analyze".
5. Verify the chart appears and anomalies (if any) are highlighted.
