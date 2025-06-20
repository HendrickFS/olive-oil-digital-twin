import paho.mqtt.client as mqtt
import time
import random
import json

def on_connect(client, userdata, flags, rc):
    client.subscribe("olive.deposits/incoming/#")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} -> {msg.payload}")

data = {
    "olive.deposits:deposit001": 25,
    "olive.deposits:deposit002": 25,
    "olive.deposits:deposit003": 25,
}

def update_data(range):
    for key, value in data.items():
        data[key] = value + random.randint(-range, range)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1884, 60)

client.loop_start()

try:
    while True:
        update_data(5)
        for thing_id, temperature in data.items():
            deposit_id = thing_id.split(":")[1]
            topic = f"olive.deposits/incoming/{deposit_id}"
            payload = json.dumps({
                "temperature": temperature,
                "thingId": thing_id
            })
            client.publish(topic, payload)
            print(f"Published: {topic} -> {payload}")
        time.sleep(5)
except KeyboardInterrupt:
    print("closing")
finally:
    client.loop_stop()
    client.disconnect()