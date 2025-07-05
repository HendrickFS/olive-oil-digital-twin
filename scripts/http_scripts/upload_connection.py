import requests
import json
import os

AUTH = ("devops", "foobar")
CONNECTIONS_DIRECTORY = "./../connections/"

def send_connection(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            path = os.path.join(directory, filename)
            with open(path, "r") as file:
                connection = json.load(file)
                url = "http://localhost:8080/devops/piggyback/connectivity"
                response = requests.post(url, json=connection, auth=AUTH)
                print(f" {response.status_code} : {response.reason}")

def upload_connections():
    if not os.path.exists(CONNECTIONS_DIRECTORY):
        print(f"Directory {CONNECTIONS_DIRECTORY} does not exist.")
        return

    send_connection(CONNECTIONS_DIRECTORY)