# server.py
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
from datetime import datetime
from config import HOST, PORT, BUFFER_SIZE, ENCODING

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexera Socket Server - Admin Dashboard")
        self.root.geometry("700x550")
        self.root.configure(bg="#1e1e2e")  # Dark theme background

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#1e1e2e")
        self.style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#89b4fa")

        # --- UI Components ---
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        self.header_label = ttk.Label(self.main_frame, text="Socket Server Monitor", style="Header.TLabel")
        self.header_label.pack(pady=(0, 20))

        # Stats Panel
        self.stats_frame = ttk.Frame(self.main_frame)
        self.stats_frame.pack(fill=tk.X, pady=10)

        self.status_label = ttk.Label(self.stats_frame, text="Status: Offline", foreground="#f38ba8")
        self.status_label.pack(side=tk.LEFT)

        self.client_count_label = ttk.Label(self.stats_frame, text="Active Connections: 0")
        self.client_count_label.pack(side=tk.RIGHT)

        # Log Area
        self.log_area = scrolledtext.ScrolledText(
            self.main_frame, 
            height=15, 
            bg="#181825", 
            fg="#cdd6f4", 
            insertbackground="white", 
            font=("Consolas", 10),
            padx=10,
            pady=10,
            borderwidth=0
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.config(state='disabled')

        # Control Panel
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=20)

        self.start_btn = tk.Button(
            self.control_frame, text="START SERVER", command=self.start_server, 
            bg="#a6e3a1", fg="#11111b", font=("Segoe UI", 9, "bold"), 
            width=15, relief=tk.FLAT, activebackground="#94e2d5"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(
            self.control_frame, text="STOP SERVER", command=self.stop_server, 
            bg="#f38ba8", fg="#11111b", font=("Segoe UI", 9, "bold"), 
            width=15, relief=tk.FLAT, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(
            self.control_frame, text="CLEAR LOGS", command=self.clear_logs, 
            bg="#89b4fa", fg="#11111b", font=("Segoe UI", 9, "bold"), 
            width=15, relief=tk.FLAT
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

        # --- Server Logic ---
        self.server_socket = None
        self.running = False
        self.clients = []

    def log(self, message):
        """Timestamped, thread-safe logging."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def update_ui_state(self):
        self.client_count_label.config(text=f"Active Connections: {len(self.clients)}")
        if self.running:
            self.status_label.config(text="Status: Online", foreground="#a6e3a1")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Status: Offline", foreground="#f38ba8")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def clear_logs(self):
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')

    def start_server(self):
        if self.running: return
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow quick restart
        
        try:
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(5)
            self.running = True
            self.update_ui_state()
            self.log(f"[*] LISTENING on {HOST}:{PORT}")
            
            threading.Thread(target=self._accept_loop, daemon=True).start()
        except Exception as e:
            self.log(f"[!] STARTUP ERROR: {e}")

    def stop_server(self):
        self.running = False
        self.log("[*] SHUTTING DOWN server...")
        
        # Close all active clients
        for client in self.clients:
            try: client.close()
            except: pass
        self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                # Use a dummy connection to break the accept loop if necessary, 
                # or just close it (closing usually triggers an exception in the accept thread)
                self.server_socket.close()
            except: pass
        
        self.update_ui_state()
        self.log("[*] Server stopped.")

    def _accept_loop(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                self.clients.append(client_socket)
                self.root.after(0, lambda: self.log(f"[+] CONNECTION: {addr}"))
                self.root.after(0, self.update_ui_state)
                
                threading.Thread(target=self._handle_client, args=(client_socket, addr), daemon=True).start()
            except:
                break

    def _handle_client(self, client_socket, addr):
        while self.running:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data: break
                
                message = data.decode(ENCODING)
                self.root.after(0, lambda: self.log(f"[{addr}] REQ: {message}"))
                
                response = f"Ack: {message}"
                client_socket.send(response.encode(ENCODING))
                self.root.after(0, lambda: self.log(f"[*] RES sent to {addr}"))
            except:
                break
        
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()
        self.root.after(0, lambda: self.log(f"[-] DISCONNECT: {addr}"))
        self.root.after(0, self.update_ui_state)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
