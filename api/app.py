from flask import Flask, jsonify, request
from flask_cors import CORS
from influxdb_client import InfluxDBClient

url = "http://localhost:9999"
token = "_Jof9SeopipTjXIdeLIoeBmtSK7TX-pLAcxu7oubrpSTuqu9KVgEyMVd4LN2h9amEFYCce1u0EBnmrYC5sU9VQ=="
org = "SustainOlive"
bucket = "DigitalTwin"

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

app = Flask(__name__)
CORS(app)

@app.route("/data", methods=["GET"])
def get_data():
    thingId = request.args.get("thingId", "")
    feature = request.args.get("feature", "")
    range_start = request.args.get("range_start", "-12h")

    query = f'from(bucket: "{bucket}") |> range(start: {range_start} ) |> filter(fn: (r) => r["deviceId"] == "{thingId}") |> filter(fn: (r) => r["_field"] == "{feature}")'
    result = query_api.query(query)
    data = []
    for table in result:
        for record in table.records:
            data.append({"time": record.get_time(), "value": record.get_value()})
    return jsonify(data)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, debug=True)