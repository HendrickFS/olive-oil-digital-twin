import random
import requests
import os
import json
from time import sleep

DITTO_API_URL = "http://localhost:8080/api/2"
AUTH = ("ditto", "ditto")

MODELS_DIRECTORY = "../../models/deposits"

def get_current_temperature(thingId):
    url = f"{DITTO_API_URL}/things/{thingId}"
    response = requests.get(url, auth=AUTH)
    if response.status_code == 200:
        data = response.json()
        return data["features"]["temperature"]["properties"]["value"]
    else:
        print(f"Error fetching temperature for {thingId}: {response.status_code}")
        return None

def update_temperature(temperature, range):
    delta = random.uniform(-range, range)
    return temperature + delta

def temperature_simulation():
    while True:
        for filename in os.listdir(MODELS_DIRECTORY):
            if filename.endswith(".json"):
                with open(os.path.join(MODELS_DIRECTORY, filename), 'r') as file:
                    data = json.load(file)
                    id = data.get("thingId")
                    temperature = get_current_temperature(id)
                    if temperature is not None:
                        new_temperature = update_temperature(temperature, 0.5)
                        new_temperature = round(new_temperature, 2)
                        data["features"]["temperature"]["properties"]["value"] = new_temperature
                        url = f"{DITTO_API_URL}/things/{id}"
                        response = requests.put(url, json=data, auth=AUTH)
                        print(f"Updated {id} -> {response.status_code} : {response.reason}")
        sleep(5)

def main():
    if not os.path.exists(MODELS_DIRECTORY):
        print(f"Directory {MODELS_DIRECTORY} does not exist.")
        return

    temperature_simulation()

main()