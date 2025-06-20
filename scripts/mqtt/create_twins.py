import os
import paho.mqtt.client as mqtt
import json
import time

def send_model(client, model, topic):
    client.publish(topic, json.dumps(model), qos=0, retain=True)
    print(f"Modelo enviado para o tópico: {topic}")

def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao Broker com código {rc}")

client = mqtt.Client()

# Configurar autenticação (se necessário)
# client.username_pw_set("username", "password")

# Defina o broker MQTT
broker = "localhost"  # ou o endereço do seu broker Mosquitto
port = 1883  # ou a porta que você configurou no broker

# Defina os callbacks
client.on_connect = on_connect

# Conectar ao broker MQTT
client.connect(broker, port, 60)

def process_files_and_send():
    folder_path = "./../models/deposits"  # Caminho da pasta com seus modelos JSON
    
    # Loop infinito que verifica os arquivos na pasta a cada 5 segundos
    while True:
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):  # Só processa arquivos JSON
                file_path = os.path.join(folder_path, filename)
                
                # Carregar o arquivo JSON
                with open(file_path, 'r') as file:
                    model = json.load(file)
                    thing_id = model.get("thingId", "unknown")
                    topic = f"eclipse-ditto-sandbox/{thing_id}/things/twin/events"  # Defina o tópico corretamente

                    # Enviar o modelo via MQTT
                    send_model(client, model, topic)
                    
                    # Opcional: Excluir ou mover o arquivo após o envio, se necessário
                    # os.remove(file_path)  # Remover o arquivo ou use shutil.move para mover
                    print(f"Arquivo processado: {filename}")
        
        # Espera de 5 segundos antes de verificar novamente
        time.sleep(5)

# Iniciar o loop MQTT e o processamento dos arquivos
client.loop_start()  # Inicia o loop do cliente MQTT

# Processar arquivos na pasta e enviar
process_files_and_send()

