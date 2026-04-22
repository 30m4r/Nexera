# server.py
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from config import HOST, PORT, BUFFER_SIZE, ENCODING

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Socket Server Dashboard")
        self.root.geometry("600x500")

        # --- UI Components ---
        # Status Frame
        self.status_frame = tk.Frame(root, pady=10)
        self.status_frame.pack(fill=tk.X)

        self.status_label = tk.Label(self.status_frame, text="Server Status: Offline", fg="red", font=("Arial", 12, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=20)

        self.client_count_label = tk.Label(self.status_frame, text="Connected Clients: 0", font=("Arial", 10))
        self.client_count_label.pack(side=tk.RIGHT, padx=20)

        # Log Area
        self.log_label = tk.Label(root, text="Activity Log:")
        self.log_label.pack(anchor=tk.W, padx=20)

        self.log_area = scrolledtext.ScrolledText(root, height=20, state='disabled', wrap=tk.WORD)
        self.log_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Controls
        self.start_btn = tk.Button(root, text="Start Server", command=self.start_server, bg="green", fg="white")
        self.start_btn.pack(pady=10)

        # --- Server Logic ---
        self.server_socket = None
        self.running = False
        self.clients = []

    def log(self, message):
        """Thread-safe logging to the GUI text area."""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def update_client_count(self):
        """Updates the UI counter."""
        self.client_count_label.config(text=f"Connected Clients: {len(self.clients)}")

    def start_server(self):
        if self.running:
            return

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(5)
            self.running = True
            
            self.status_label.config(text="Server Status: Online (Listening)", fg="green")
            self.start_btn.config(state=tk.DISABLED)
            self.log(f"[*] Server started on {HOST}:{PORT}")
            
            threading.Thread(target=self._accept_loop, daemon=True).start()
        except Exception as e:
            self.log(f"[!] Startup Error: {e}")

    def _accept_loop(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                self.clients.append(client_socket)
                
                # UI Updates must be done carefully (though simple labels are usually okay in Tkinter threads, logging is custom)
                self.root.after(0, lambda: self.log(f"[+] Client connected: {addr}"))
                self.root.after(0, self.update_client_count)
                
                threading.Thread(target=self._handle_client, args=(client_socket, addr), daemon=True).start()
            except:
                break

    def _handle_client(self, client_socket, addr):
        while self.running:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                message = data.decode(ENCODING)
                self.root.after(0, lambda: self.log(f"[{addr}] Request: {message}"))
                
                response = f"Ack: {message}"
                client_socket.send(response.encode(ENCODING))
                self.root.after(0, lambda: self.log(f"[*] Sent response to {addr}"))
                
            except:
                break
        
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()
        self.root.after(0, lambda: self.log(f"[-] Client disconnected: {addr}"))
        self.root.after(0, self.update_client_count)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
