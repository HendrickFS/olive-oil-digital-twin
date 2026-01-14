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
    latest = request.args.get("latest", "false").lower() in {"true", "1", "yes"}
    dedup = request.args.get("dedup", "false").lower() in {"true", "1", "yes"}
    
    # Get data using same logic as /data endpoint
    query = _build_query(thingId, feature, range_start, latest, dedup)
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