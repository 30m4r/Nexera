# client.py
import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime
from config import HOST, PORT, BUFFER_SIZE, ENCODING

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexera Client Interface")
        self.root.geometry("450x600")
        self.root.configure(bg="#1e1e2e")

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#1e1e2e")
        self.style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#fab387")

        # --- UI Components ---
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header & Status
        self.header_label = ttk.Label(self.main_frame, text="Socket Client Terminal", style="Header.TLabel")
        self.header_label.pack(pady=(0, 10))

        self.status_label = ttk.Label(self.main_frame, text="Status: DISCONNECTED", foreground="#f38ba8", font=("Segoe UI", 9, "bold"))
        self.status_label.pack(pady=(0, 15))

        # Output Display
        self.output_area = scrolledtext.ScrolledText(
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
        self.output_area.pack(fill=tk.BOTH, expand=True)
        self.output_area.config(state='disabled')

        # Input Section
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=15)

        self.message_entry = tk.Entry(
            self.input_frame, 
            bg="#313244", 
            fg="#cdd6f4", 
            insertbackground="white", 
            relief=tk.FLAT, 
            font=("Segoe UI", 10),
            disabledbackground="#1e1e2e"
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.message_entry.bind("<Return>", lambda event: self.send_message())
        self.message_entry.config(state=tk.DISABLED)

        self.send_btn = tk.Button(
            self.input_frame, text="SEND", command=self.send_message, 
            bg="#89b4fa", fg="#11111b", font=("Segoe UI", 8, "bold"), 
            relief=tk.FLAT, width=8, state=tk.DISABLED
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Bottom Controls
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X)

        self.connect_btn = tk.Button(
            self.control_frame, text="CONNECT", command=self.connect, 
            bg="#a6e3a1", fg="#11111b", font=("Segoe UI", 9, "bold"), 
            relief=tk.FLAT, width=15
        )
        self.connect_btn.pack(side=tk.LEFT, pady=10)

        self.disconnect_btn = tk.Button(
            self.control_frame, text="DISCONNECT", command=self.disconnect, 
            bg="#f38ba8", fg="#11111b", font=("Segoe UI", 9, "bold"), 
            relief=tk.FLAT, width=15, state=tk.DISABLED
        )
        self.disconnect_btn.pack(side=tk.LEFT, padx=10, pady=10)

        self.clear_btn = tk.Button(
            self.control_frame, text="CLEAR", command=self.clear_chat, 
            bg="#6c7086", fg="#ffffff", font=("Segoe UI", 9), 
            relief=tk.FLAT, width=8
        )
        self.clear_btn.pack(side=tk.RIGHT, pady=10)

        # --- Client Logic ---
        self.client_socket = None
        self.connected = False

    def log(self, message, prefix="SYSTEM"):
        """Thread-safe logging to the UI."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, f"[{timestamp}] {prefix}: {message}\n")
        self.output_area.see(tk.END)
        self.output_area.config(state='disabled')

    def clear_chat(self):
        self.output_area.config(state='normal')
        self.output_area.delete(1.0, tk.END)
        self.output_area.config(state='disabled')

    def update_ui_state(self):
        if self.connected:
            self.status_label.config(text="Status: CONNECTED", foreground="#a6e3a1")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.send_btn.config(state=tk.NORMAL)
            self.message_entry.config(state=tk.NORMAL)
            self.message_entry.focus_set()
        else:
            self.status_label.config(text="Status: DISCONNECTED", foreground="#f38ba8")
            self.connect_btn.config(state=tk.NORMAL)
            self.disconnect_btn.config(state=tk.DISABLED)
            self.send_btn.config(state=tk.DISABLED)
            self.message_entry.config(state=tk.DISABLED)

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.connected = True
            self.update_ui_state()
            self.log("Secure connection established.")
            
            # Start background listener thread
            threading.Thread(target=self._receive_loop, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Unable to reach server:\n{e}")

    def disconnect(self):
        self.connected = False
        if self.client_socket:
            try: self.client_socket.close()
            except: pass
        self.update_ui_state()
        self.log("Disconnected from host.")

    def send_message(self):
        message = self.message_entry.get().strip()
        if not message or not self.connected:
            return

        try:
            self.client_socket.send(message.encode(ENCODING))
            self.log(message, prefix="YOU")
            self.message_entry.delete(0, tk.END)
        except Exception as e:
            self.log(f"Send error: {e}")
            self.disconnect()

    def _receive_loop(self):
        """Continuously listens for server data without blocking UI."""
        while self.connected:
            try:
                data = self.client_socket.recv(BUFFER_SIZE)
                if not data:
                    self.root.after(0, lambda: self.log("Server closed the connection."))
                    self.root.after(0, self.disconnect)
                    break
                
                response = data.decode(ENCODING)
                self.root.after(0, lambda: self.log(response, prefix="SERVER"))
            except:
                if self.connected:
                    self.root.after(0, lambda: self.log("Lost connection to server."))
                    self.root.after(0, self.disconnect)
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()
