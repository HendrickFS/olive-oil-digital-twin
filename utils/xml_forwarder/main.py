import socket
import xml.etree.ElementTree as ET

def process_xml(data):
    try:
        # Parse the XML data
        root = ET.fromstring(data)
        # Process the XML as needed
        print("XML received:", ET.tostring(root))
    except ET.ParseError as e:
        print("error to analyse XML:", e)

def start_server():
    host = '0.0.0.0'  # Ou você pode usar o IP específico
    port = 6100

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server TCP listening at port {port}...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connection {addr} established.")
                data = b""
                while True:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    data += chunk

                # Converte os dados recebidos para string
                xml_data = data.decode('utf-8')
                process_xml(xml_data)

if __name__ == "__main__":
    start_server()