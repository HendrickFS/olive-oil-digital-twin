import requests
import os
import json

DITTO_API_URL = "http://docker-gateway-1:8080/api/2"
AUTH = ("ditto", "ditto")
DEV_AUTH = ("devops", "foobar")

MODELS_DIRECTORY = "/app/models_backup/"
CONNECTIONS_DIRECTORY = "/app/connections_backup/"

def get_models():
    url = f"{DITTO_API_URL}/things"
    response = requests.get(url, auth=AUTH)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching models: {response.status_code}")
        return []
    
def get_connections():
    url = f"{DITTO_API_URL}/connections"
    response = requests.get(url, auth=DEV_AUTH)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching connections: {response.status_code}")
        return []
    

def backup_models():
    models = get_models()
    if not models:
        print("No models found to backup.")
        return
    
    if not os.path.exists(MODELS_DIRECTORY):
        os.makedirs(MODELS_DIRECTORY)
    
    for model in models:
        print(f"Backing up model: {model.get('thingId')}")
        model_id = model.get("thingId")
        model_name = model_id.split(":")[1]
        filename = os.path.join(MODELS_DIRECTORY, f"{model_name}.json")
        if filename in os.listdir(MODELS_DIRECTORY):
            os.remove(filename)
        with open(filename, 'w') as f:
            json.dump(model, f, indent=4)

    print(f"Backup completed. {len(models)} models saved to {MODELS_DIRECTORY}")

def backup_connections():
    connections = get_connections()
    if not connections:
        print("No connections found to backup.")
        return
    
    if not os.path.exists(CONNECTIONS_DIRECTORY):
        os.makedirs(CONNECTIONS_DIRECTORY)
    
    for connection in connections:
        print(f"Backing up connection: {connection.get('id')}")
        connection_id = connection.get("id")
        filename = os.path.join(CONNECTIONS_DIRECTORY, f"{connection_id}.json")
        if filename in os.listdir(CONNECTIONS_DIRECTORY):
            os.remove(filename)
        with open(filename, 'w') as f:
            json.dump(connection, f, indent=4)

    print(f"Backup completed. {len(connections)} connections saved to {CONNECTIONS_DIRECTORY}")


if __name__ == "__main__":
    backup_models()
    backup_connections()