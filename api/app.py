from flask import Flask, jsonify, request
from flask_cors import CORS
from influxdb_client import InfluxDBClient

url = "http://193.136.195.37:9999"
# url = "http://192.168.56.1:9999"
token = "_Jof9SeopipTjXIdeLIoeBmtSK7TX-pLAcxu7oubrpSTuqu9KVgEyMVd4LN2h9amEFYCce1u0EBnmrYC5sU9VQ=="
org = "SustainOlive"
bucket = "DigitalTwin"

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

app = Flask(__name__)
CORS(app, resources={r"/data*": {"origins": "*"}, r"/ml*": {"origins": "*"}}, supports_credentials=True)

@app.route("/data", methods=["GET"])
def get_data():
    thingId = request.args.get("thingId", "")
    feature = request.args.get("feature", "")
    range_start = request.args.get("range_start", "-24h")

    query = f'from(bucket: "{bucket}") |> range(start: {range_start} ) |> filter(fn: (r) => r["deviceId"] == "{thingId}") |> filter(fn: (r) => r["_field"] == "{feature}")'
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
    
    # Get data using same logic as /data endpoint
    query = f'from(bucket: "{bucket}") |> range(start: {range_start} ) |> filter(fn: (r) => r["deviceId"] == "{thingId}") |> filter(fn: (r) => r["_field"] == "{feature}")'
    result = query_api.query(query)
    data = []
    for table in result:
        for record in table.records:
            data.append({"time": record.get_time(), "value": record.get_value()})
    
    # TODO: Add your anomaly detection logic here
    # For now, just return basic info
    response = {
        "device": thingId,
        "feature": feature,
        "data_points": len(data),
        "anomaly_detected": False,
        "message": "Anomaly detection not implemented yet"
    }
    
    return jsonify(response)

@app.route("/ml/stats", methods=["GET"])
def get_stats():
    """Get basic statistics for sensor data"""
    thingId = request.args.get("thingId", "")
    feature = request.args.get("feature", "")
    range_start = request.args.get("range_start", "-24h")
    
    # Get data
    query = f'from(bucket: "{bucket}") |> range(start: {range_start} ) |> filter(fn: (r) => r["deviceId"] == "{thingId}") |> filter(fn: (r) => r["_field"] == "{feature}")'
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