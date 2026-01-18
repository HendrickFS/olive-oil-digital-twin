from flask import Flask, jsonify, request
from flask_cors import CORS
from influxdb_client import InfluxDBClient
import numpy as np
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.anomaly_detection import AnomalyDetector

url = "http://193.136.195.37:9999"
# url = "http://192.168.56.1:9999"
token = "_Jof9SeopipTjXIdeLIoeBmtSK7TX-pLAcxu7oubrpSTuqu9KVgEyMVd4LN2h9amEFYCce1u0EBnmrYC5sU9VQ=="
org = "SustainOlive"
bucket = "DigitalTwin"

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

app = Flask(__name__)
CORS(app, resources={r"/data*": {"origins": "*"}, r"/ml*": {"origins": "*"}}, supports_credentials=True)

def _build_query(thing_id: str, feature: str, range_start: str, latest: bool = False, dedup: bool = False) -> str:
    base = f'from(bucket: "{bucket}") |> range(start: {range_start} ) |> filter(fn: (r) => r["thingId"] == "{thing_id}") |> filter(fn: (r) => r["_field"] == "{feature}")'
    
    if latest:
        return base + " |> last()"
    
    # For "state" feature, apply 5-minute aggregation window to reduce data volume
    if feature == "state":
        return base + ' |> aggregateWindow(every: 5m, fn: last, createEmpty: false)'
    
    if dedup:
        # Collapse points that share the exact same timestamp by taking the last written value
        return base + " |> group(columns: [\"_time\", \"thingId\", \"_field\", \"topic\", \"host\"]) |> last() |> sort(columns: [\"_time\"] )"
    
    return base

@app.route("/data", methods=["GET"])
def get_data():
    thingId = request.args.get("thingId", "")
    feature = request.args.get("feature", "")
    range_start = request.args.get("range_start", "-24h")
    latest = request.args.get("latest", "false").lower() in {"true", "1", "yes"}
    dedup = request.args.get("dedup", "false").lower() in {"true", "1", "yes"}

    query = _build_query(thingId, feature, range_start, latest, dedup)
    result = query_api.query(query)
    data = []
    for table in result:
        for record in table.records:
            data.append({"time": record.get_time(), "value": record.get_value()})
    return jsonify(data)

@app.route("/ml/health", methods=["GET"])
def ml_health():
    """Check if ML functionality is available"""
    return jsonify({"status": "ML endpoints available", "version": "1.0"})

@app.route("/ml/anomaly", methods=["GET"])
def check_anomaly():
    """Check for anomalies in sensor data"""
    thingId = request.args.get("thingId", "")
    feature = request.args.get("feature", "")
    range_start = request.args.get("range_start", "-1h")
    training_range = request.args.get("training_range", "-24h")
    latest = request.args.get("latest", "false").lower() in {"true", "1", "yes"}
    dedup = request.args.get("dedup", "false").lower() in {"true", "1", "yes"}
    
    if not thingId or not feature:
        return jsonify({"error": "thingId and feature parameters required"}), 400
    
    try:
        # Step 1: Fetch historical training data
        training_query = _build_query(thingId, feature, training_range, latest=False, dedup=dedup)
        training_result = query_api.query(training_query)
        training_values = []
        for table in training_result:
            for record in table.records:
                val = record.get_value()
                if isinstance(val, (int, float)):
                    training_values.append(val)
        
        if len(training_values) < 10:
            return jsonify({
                "error": "Insufficient training data (need at least 10 points)",
                "available_points": len(training_values)
            }), 400
        
        # Step 2: Train Isolation Forest on historical data
        cache_key = f"{thingId}_{feature}"
        detector = AnomalyDetector(contamination=0.1)
        detector.fit(training_values, cache_key)
        
        # Step 3: Fetch prediction data in requested range
        prediction_query = _build_query(thingId, feature, range_start, latest=latest, dedup=dedup)
        prediction_result = query_api.query(prediction_query)
        
        # Collect data points with timestamps
        data_points = []
        for table in prediction_result:
            for record in table.records:
                val = record.get_value()
                if isinstance(val, (int, float)):
                    data_points.append({
                        "time": record.get_time(),
                        "value": val
                    })
        
        if not data_points:
            return jsonify({
                "device": thingId,
                "feature": feature,
                "data_points": 0,
                "anomalies": [],
                "message": "No data found in requested range"
            }), 200
        
        # Step 4: Get predictions and anomaly scores
        values = [pt["value"] for pt in data_points]
        predictions = detector.predict(values)
        scores = detector.predict_proba(values)
        
        # Build response with anomaly information
        anomalies = []
        for i, point in enumerate(data_points):
            is_anomaly = predictions[i] == -1
            anomaly_score = scores[i]
            
            anomalies.append({
                "time": point["time"],
                "value": point["value"],
                "anomaly": is_anomaly,
                "score": float(anomaly_score)  # Lower score = more anomalous
            })
        
        # Count anomalies
        anomaly_count = sum(1 for a in anomalies if a["anomaly"])
        
        response = {
            "device": thingId,
            "feature": feature,
            "training_points": len(training_values),
            "prediction_points": len(data_points),
            "anomalies_detected": anomaly_count,
            "anomaly_percentage": round(100 * anomaly_count / len(data_points), 2) if data_points else 0,
            "data": anomalies
        }
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"Error in /ml/anomaly: {error_msg}")
        logger.error(error_trace)
        return jsonify({"error": error_msg, "type": type(e).__name__}), 500

@app.route("/ml/stats", methods=["GET"])
def get_stats():
    """Get basic statistics for sensor data"""
    thingId = request.args.get("thingId", "")
    feature = request.args.get("feature", "")
    range_start = request.args.get("range_start", "-24h")
    latest = request.args.get("latest", "false").lower() in {"true", "1", "yes"}
    dedup = request.args.get("dedup", "false").lower() in {"true", "1", "yes"}
    
    # Get data
    query = _build_query(thingId, feature, range_start, latest, dedup)
    result = query_api.query(query)
    values = []
    for table in result:
        for record in table.records:
            values.append(record.get_value())
    
    if not values:
        return jsonify({"error": "No data found"})
    
    # Calculate basic stats
    stats = {
        "device": thingId,
        "feature": feature,
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "average": sum(values) / len(values)
    }
    
    return jsonify(stats)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5555, debug=False)