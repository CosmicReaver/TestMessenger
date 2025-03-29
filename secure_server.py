import socket
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
import time
from crypto_utils import decrypt_file

HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 65432
BUFFER_SIZE = 4096
PASSWORD = "strongpassword"  # Encryption key
clients = {}

def start_server():
    """Start the server and listen for connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    log_message("✅ Server started. Waiting for connections...", "info")
    while True:
        client_socket, addr = server_socket.accept()
        client_name = client_socket.recv(1024).decode()
        clients[client_socket] = client_name
        log_message(f"🔵 {client_name} connected from {addr[0]}:{addr[1]}", "success")
        update_client_list()
        threading.Thread(target=handle_client, args=(client_socket, client_name), daemon=True).start()

def handle_client(client_socket, client_name):
    """Handle incoming messages from a client."""
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            if msg.startswith("MSG:"):
                broadcast_message(msg[4:], client_name)
            elif msg.startswith("FILE:"):
                _, filename, file_size = msg.split(":")
                receive_file(client_socket, filename, int(file_size))
        except:
            break
    log_message(f"🔴 {client_name} disconnected", "error")
    clients.pop(client_socket)
    update_client_list()
    client_socket.close()

def broadcast_message(message, sender):
    """Send a message to all connected clients."""
    timestamp = time.strftime("[%H:%M:%S] ")
    formatted_message = f"{timestamp}{sender}: {message}"
    log_message(formatted_message, "client")
    for client in clients.keys():
        client.send(f"MSG:{formatted_message}".encode())

def receive_file(client_socket, filename, file_size):
    """Receive a file from a client with progress."""
    encrypted_file = "received_" + filename
    with open(encrypted_file, "wb") as f:
        remaining = file_size
        progress_win = tk.Toplevel(root)
        progress_win.title("Receiving File")
        progress_label = tk.Label(progress_win, text=f"Receiving {filename}")
        progress_label.pack()
        progress_bar = ttk.Progressbar(progress_win, length=300, mode='determinate')
        progress_bar.pack()
        while remaining:
            chunk = client_socket.recv(min(BUFFER_SIZE, remaining))
            if not chunk:
                break
            f.write(chunk)
            remaining -= len(chunk)
            progress_bar['value'] = ((file_size - remaining) / file_size) * 100
            root.update_idletasks()
        progress_win.destroy()
    decrypted_file = encrypted_file.replace(".enc", "")
    decrypt_file(encrypted_file, decrypted_file, PASSWORD)
    log_message(f"✅ File '{filename}' received and decrypted.", "success")

def log_message(message, tag="info"):
    """Log a message to the GUI chat box."""
    chat_box.insert(tk.END, f"{message}\n", tag)
    chat_box.yview(tk.END)

def update_client_list():
    """Update the GUI client list display."""
    client_list.delete(0, tk.END)
    for client in clients.values():
        client_list.insert(tk.END, client)

# GUI Setup
root = tk.Tk()
root.title("Secure Chat Server")
root.geometry("500x500")
root.configure(bg="#f0f0f0")

chat_box = scrolledtext.ScrolledText(root, width=60, height=20, state=tk.NORMAL, wrap=tk.WORD)
chat_box.pack(pady=10, padx=10)
chat_box.tag_config("info", foreground="blue")
chat_box.tag_config("success", foreground="darkgreen")
chat_box.tag_config("error", foreground="red")
chat_box.tag_config("client", foreground="black")

client_list_label = tk.Label(root, text="Connected Clients:")
client_list_label.pack()
client_list = tk.Listbox(root, height=5)
client_list.pack()

threading.Thread(target=start_server, daemon=True).start()
root.mainloop()
