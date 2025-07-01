import paho.mqtt.client as mqtt
import time
import random
import json

def on_connect(client, userdata, flags, rc):
    client.subscribe("olive.deposits/incoming/#")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} -> {msg.payload}")

data = {
    "olive.deposits:deposit001": {
        "temperature": 25,
        "humidity": 5,
        "mq": [5] * 9
    },
    "olive.deposits:deposit002": {
        "temperature": 25,
        "humidity": 5,
        "mq": [5] * 9
    },
    "olive.deposits:deposit003": {
        "temperature": 25,
        "humidity": 5,
        "mq": [5] * 9
    },
}

def update_data(range_temp, range_hum, range_mq):
    for key, values in data.items():
        # Atualiza temperatura
        values["temperature"] += random.randint(-range_temp, range_temp)
        # Atualiza humidade com limite 0-10
        values["humidity"] = max(0, min(10, values["humidity"] + random.randint(-range_hum, range_hum)))
        # Atualiza cada valor do array mq, com limite 0-10
        values["mq"] = [
            max(0, min(10, val + random.randint(-range_mq, range_mq))) 
            for val in values["mq"]
        ]

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1884, 60)

client.loop_start()

try:
    while True:
        update_data(3, 2, 2)
        for thing_id, values in data.items():
            deposit_id = thing_id.split(":")[1]
            topic = f"olive.deposits/incoming/{deposit_id}"
            payload = json.dumps({
                "thingId": thing_id,
                "temperature": values["temperature"],
                "humidity": values["humidity"],
                "mq": values["mq"]
            })
            client.publish(topic, payload)
            print(f"Published: {topic} -> {payload}")
        time.sleep(5)
except KeyboardInterrupt:
    print("closing")
finally:
    client.loop_stop()
    client.disconnect()
