# server.py
import socket
import threading
from config import HOST, PORT, BUFFER_SIZE, ENCODING

class MultiClientServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = []

    def start_server(self):
        """Initializes and starts listening for connections."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            print(f"[*] Server listening on {self.host}:{self.port}")
            
            # Start accepting clients in a separate thread to keep it non-blocking
            threading.Thread(target=self._accept_loop, daemon=True).start()
        except Exception as e:
            print(f"[!] Failed to start server: {e}")

    def _accept_loop(self):
        """Continuously accepts new client connections."""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"[+] New connection from {client_address}")
                self.clients.append(client_socket)
                
                # Start a handler thread for this specific client
                threading.Thread(target=self._handle_client, args=(client_socket, client_address), daemon=True).start()
            except Exception as e:
                if self.running:
                    print(f"[!] Error accepting client: {e}")
                break

    def _handle_client(self, client_socket, address):
        """Processes messages from a single client."""
        while self.running:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                message = data.decode(ENCODING)
                print(f"[{address}] Received: {message}")
                
                # Prepare response
                response = f"Server received: {message}"
                client_socket.send(response.encode(ENCODING))
                print(f"[*] Sent response to {address}")
            except (ConnectionResetError, BrokenPipeError):
                break
            except Exception as e:
                print(f"[!] Error handling client {address}: {e}")
                break
        
        print(f"[-] Client {address} disconnected")
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()

    def stop_server(self):
        """Gracefully shuts down the server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for client in self.clients:
            client.close()
        print("[*] Server stopped")

if __name__ == "__main__":
    server = MultiClientServer()
    server.start_server()
    
    # Keep main thread alive for CLI testing
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.stop_server()
