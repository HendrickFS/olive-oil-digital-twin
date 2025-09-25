"""
MQTT Connection Test Script for Olive Oil Digital Twin
Simulates sensor data from deposit devices and publishes to MQTT broker.
"""

import paho.mqtt.client as mqtt
import time
import random
import json

# MQTT Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1884

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe("deposit/incoming/#")

def on_message(client, userdata, msg):
    print(f"Received: {msg.topic} -> {msg.payload.decode()}")

# Sensor data for deposits
data = {
    "olive.production:deposit001": {"temperature": 25, "humidity": 50, "mq": [5] * 9},
    "olive.production:deposit002": {"temperature": 25, "humidity": 50, "mq": [5] * 9},
    "olive.production:deposit003": {"temperature": 25, "humidity": 50, "mq": [5] * 9},
}

def update_data(variation=2):
    """Update sensor values with random variations"""
    for values in data.values():
        # Update temperature
        values["temperature"] += random.uniform(-variation, variation)
        # Update humidity (0-100%)
        values["humidity"] = max(0, min(100, values["humidity"] + random.uniform(-variation, variation)))
        # Update MQ sensors (0-10 range)
        values["mq"] = [max(0, min(10, val + random.uniform(-variation, variation))) for val in values["mq"]]

# Setup MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to MQTT broker...")
client.connect(MQTT_HOST, MQTT_PORT, 60)

client.loop_start()

print("Starting sensor simulation... (Press Ctrl+C to stop)")
try:
    while True:
        update_data()
        
        for thing_id, values in data.items():
            deposit_id = thing_id.split(":")[1]
            topic = f"deposit/incoming/{deposit_id}"
            payload = json.dumps({
                "thingId": thing_id,
                "temperature": round(values["temperature"], 1),
                "humidity": round(values["humidity"], 1),
                "mq": [round(val, 1) for val in values["mq"]]
            })
            client.publish(topic, payload)
            print(f"Published: {topic} -> {payload}")
        time.sleep(5)

except KeyboardInterrupt:
    print("\nStopping simulation...")
finally:
    client.loop_stop()
    client.disconnect()
    print("Disconnected from MQTT broker")
