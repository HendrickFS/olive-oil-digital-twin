import requests
import os
import json
import datetime

DITTO_API_URL = "http://docker-gateway-1:8080/api/2"
AUTH = ("ditto", "ditto")
DEV_AUTH = ("devops", "foobar")

MODELS_DIRECTORY = "/app/models_backup"
CONNECTIONS_DIRECTORY = "/app/connections_backup"

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_models():
    log_message("Fetching models from Ditto API...")
    url = f"{DITTO_API_URL}/things"
    try:
        response = requests.get(url, auth=AUTH, timeout=30)
        if response.status_code == 200:
            models = response.json()
            log_message(f"Successfully fetched {len(models)} models")
            return models
        else:
            log_message(f"Error fetching models: HTTP {response.status_code}")
            return []
    except Exception as e:
        log_message(f"Exception while fetching models: {str(e)}")
        return []
    
def get_connections():
    log_message("Fetching connections from Ditto API...")
    url = f"{DITTO_API_URL}/connections"
    try:
        response = requests.get(url, auth=DEV_AUTH, timeout=30)
        if response.status_code == 200:
            connections = response.json()
            log_message(f"Successfully fetched {len(connections)} connections")
            return connections
        else:
            log_message(f"Error fetching connections: HTTP {response.status_code}")
            return []
    except Exception as e:
        log_message(f"Exception while fetching connections: {str(e)}")
        return []
    

def backup_models():
    log_message("Starting models backup...")
    models = get_models()
    if not models:
        log_message("No models found to backup.")
        return
    
    try:
        if not os.path.exists(MODELS_DIRECTORY):
            os.makedirs(MODELS_DIRECTORY)
            log_message(f"Created models directory: {MODELS_DIRECTORY}")
        
        for model in models:
            model_id = model.get("thingId")
            if not model_id:
                log_message("Warning: Model without thingId found, skipping...")
                continue
                
            log_message(f"Backing up model: {model_id}")
            model_name = model_id.split(":")[1] if ":" in model_id else model_id
            filename = os.path.join(MODELS_DIRECTORY, f"{model_name}.json")
            
            if os.path.exists(filename):
                os.remove(filename)
                
            with open(filename, 'w') as f:
                json.dump(model, f, indent=4)

        log_message(f"Models backup completed. {len(models)} models saved to {MODELS_DIRECTORY}")
    except Exception as e:
        log_message(f"Error during models backup: {str(e)}")

def backup_connections():
    log_message("Starting connections backup...")
    connections = get_connections()
    if not connections:
        log_message("No connections found to backup.")
        return
    
    try:
        if not os.path.exists(CONNECTIONS_DIRECTORY):
            os.makedirs(CONNECTIONS_DIRECTORY)
            log_message(f"Created connections directory: {CONNECTIONS_DIRECTORY}")
        
        for connection in connections:
            connection_id = connection.get("id")
            if not connection_id:
                log_message("Warning: Connection without id found, skipping...")
                continue
                
            log_message(f"Backing up connection: {connection_id}")
            filename = os.path.join(CONNECTIONS_DIRECTORY, f"{connection_id}.json")
            
            if os.path.exists(filename):
                os.remove(filename)
                
            with open(filename, 'w') as f:
                json.dump(connection, f, indent=4)

        log_message(f"Connections backup completed. {len(connections)} connections saved to {CONNECTIONS_DIRECTORY}")
    except Exception as e:
        log_message(f"Error during connections backup: {str(e)}")


if __name__ == "__main__":
    log_message("=== Starting Digital Twin Backup Process ===")
    backup_models()
    backup_connections()
    log_message("=== Backup Process Completed ===")