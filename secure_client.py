import socket
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog, messagebox, ttk
import time
from crypto_utils import encrypt_file

SERVER_HOST = '192.168.50.191'  # Default server IP
PORT = 65432
BUFFER_SIZE = 4096
PASSWORD = "strongpassword"  # Encryption key
client_socket = None
client_name = ""
reconnect_attempts = 0  # Track retries

def connect_to_server():
    """Attempt to connect to the server, retrying with limits."""
    global client_socket, reconnect_attempts
    while reconnect_attempts < 5:  # Retry up to 5 times
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, PORT))
            chat_box.insert(tk.END, "✅ Connected to server!\n", "success")
            client_socket.send(client_name.encode())
            threading.Thread(target=receive_messages, daemon=True).start()
            reconnect_attempts = 0  # Reset on success
            return
        except Exception as e:
            reconnect_attempts += 1
            time.sleep(3)  # Retry delay
            chat_box.insert(tk.END, f"⚠️ Connection failed. Retrying... ({reconnect_attempts}/5)\n", "error")
    chat_box.insert(tk.END, "❌ Could not connect to server. Check your network.\n", "error")

def receive_messages():
    """Handle incoming messages from the server."""
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            if msg.startswith("MSG:"):
                chat_box.insert(tk.END, f"{msg[4:]}\n", "client")
            elif msg.startswith("FILE:"):
                _, filename, file_size = msg.split(":")
                receive_file(filename, int(file_size))
        except:
            chat_box.insert(tk.END, "❌ Disconnected from server! Attempting to reconnect...\n", "error")
            connect_to_server()
            break

def send_message():
    """Send a text message to the server."""
    message = message_entry.get().strip()
    if message and client_socket:
        timestamp = time.strftime("[%H:%M:%S] ")
        chat_box.insert(tk.END, f"{timestamp}You: {message}\n", "self")
        client_socket.send(f"MSG:{timestamp}{client_name}: {message}".encode())
        message_entry.delete(0, tk.END)

def send_file():
    """Encrypt and send a file to the server with progress."""
    filename = filedialog.askopenfilename()
    if not filename or not client_socket:
        return

    encrypted_file = filename + ".enc"
    encrypt_file(filename, encrypted_file, PASSWORD)
    file_size = os.path.getsize(encrypted_file)

    try:
        client_socket.send(f"FILE:{os.path.basename(encrypted_file)}:{file_size}".encode())
