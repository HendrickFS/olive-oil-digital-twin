import requests
import json
import os

DITTO_API_URL = "http://localhost:8080/api/2"
AUTH = ("ditto", "ditto")
POLICY_DIRECTORY = "./../models/policies"

def send_policy(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            path = os.path.join(directory, filename)
            with open(path, "r") as file:
                policy = json.load(file)
                url = f"{DITTO_API_URL}/policies/{policy['policyId']}"
                response = requests.put(url, json=policy, auth=AUTH)
                print(f"{policy['policyId']} -> {response.status_code} : {response.reason}")

def upload_policy():
    if not os.path.exists(POLICY_DIRECTORY):
        print(f"Directory {POLICY_DIRECTORY} does not exist.")
        return

    send_policy(POLICY_DIRECTORY)