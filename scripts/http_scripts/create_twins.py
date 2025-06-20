import os
import json
import requests

DITTO_API_URL = "http://localhost:8080/api/2"
AUTH = ("ditto", "ditto")

MODELS_DIRECTORY = "./../models/deposits"

def upload_models(directory):
    for filename in os.listdir(directory):
        print(f"Processing {filename}")
        if filename.endswith(".json"):
            path = os.path.join(directory, filename)
            with open(path, "r") as file:
                thing = json.load(file)
                url = f"{DITTO_API_URL}/things/{thing['thingId']}"
                response = requests.put(url, json=thing, auth=AUTH)
                print(f"{thing['thingId']} -> {response.status_code} : {response.reason}")

def create_twins():
    if not os.path.exists(MODELS_DIRECTORY):
        print(f"Directory {MODELS_DIRECTORY} does not exist.")
        return

    upload_models(MODELS_DIRECTORY)


create_twins()