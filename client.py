# client.py
import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext
from config import HOST, PORT, BUFFER_SIZE, ENCODING

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Socket Client")
        self.root.geometry("400x500")

        # --- UI Components ---
        # Connection Status
        self.status_label = tk.Label(root, text="Status: Disconnected", fg="red")
        self.status_label.pack(pady=5)

        # Message Output Area
        self.output_area = scrolledtext.ScrolledText(root, height=15, state='disabled', wrap=tk.WORD)
        self.output_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Input Area
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill=tk.X, padx=20, pady=10)

        self.message_entry = tk.Entry(self.input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = tk.Button(self.input_frame, text="Send", command=self.send_message, state=tk.DISABLED)
        self.send_btn.pack(side=tk.RIGHT)

        # Connect Button
        self.connect_btn = tk.Button(root, text="Connect to Server", command=self.connect)
        self.connect_btn.pack(pady=10)

        # --- Client Logic ---
        self.client_socket = None

    def log_response(self, message):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, f"Server: {message}\n")
        self.output_area.see(tk.END)
        self.output_area.config(state='disabled')

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            
            self.status_label.config(text="Status: Connected", fg="green")
            self.connect_btn.config(state=tk.DISABLED)
            self.send_btn.config(state=tk.NORMAL)
            self.log_response("Connected to server successfully.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")

    def send_message(self):
        message = self.message_entry.get().strip()
        if not message:
            return

        if not self.client_socket:
            return

        try:
            self.client_socket.send(message.encode(ENCODING))
            self.message_entry.delete(0, tk.END)
            
            # Wait for response (Note: In a more complex app, this should be in a thread to avoid UI freezing)
            response = self.client_socket.recv(BUFFER_SIZE).decode(ENCODING)
            self.log_response(response)
        except Exception as e:
            self.log_response(f"Error: {e}")
            self.status_label.config(text="Status: Disconnected", fg="red")
            self.send_btn.config(state=tk.DISABLED)
            self.connect_btn.config(state=tk.NORMAL)
            self.client_socket = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()
