# client.py
import socket
from config import HOST, PORT, BUFFER_SIZE, ENCODING

class SocketClient:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect_to_server(self):
        """Establishes connection to the server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"[+] Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[!] Connection failed: {e}")
            return False

    def send_message(self, message):
        """Sends a message to the server and returns the response."""
        if not self.client_socket:
            print("[!] Not connected to server.")
            return None
        
        try:
            self.client_socket.send(message.encode(ENCODING))
            response = self.client_socket.recv(BUFFER_SIZE).decode(ENCODING)
            return response
        except Exception as e:
            print(f"[!] Failed to send/receive data: {e}")
            return None

    def disconnect(self):
        """Closes the socket connection."""
        if self.client_socket:
            self.client_socket.close()
            print("[*] Disconnected from server.")

if __name__ == "__main__":
    client = SocketClient()
    if client.connect_to_server():
        print("Type 'exit' to quit.")
        while True:
            msg = input("Enter message: ")
            if msg.lower() == 'exit':
                break
            
            resp = client.send_message(msg)
            if resp:
                print(f"Received from server: {resp}")
            else:
                print("[!] Server connection lost.")
                break
        client.disconnect()
