import socket
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import time

SERVER_HOST = '192.168.50.191'  # Default server IP
PORT = 65432
BUFFER_SIZE = 8192  # Increased buffer size for better performance
client_socket = None
client_name = None
reconnect_attempts = 0  # Track retries

def connect_to_server():
    """Attempt to connect to the server with limited retries."""
    global client_socket, reconnect_attempts
    while reconnect_attempts < 5:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)  # Set timeout to prevent blocking
            client_socket.connect((SERVER_HOST, PORT))
            client_socket.settimeout(None)  # Remove timeout after connecting
            update_chat("✅ Connected to server!\n", "success")
            update_chat("📢 Type your NAME as the first message!\n", "info")

            threading.Thread(target=receive_messages, daemon=True).start()
            reconnect_attempts = 0  # Reset retries
            return
        except Exception:
            reconnect_attempts += 1
            time.sleep(3)
            update_chat(f"⚠️ Connection failed. Retrying... ({reconnect_attempts}/5)\n", "error")
    update_chat("❌ Could not connect to server. Check your network.\n", "error")

def receive_messages():
    """Continuously receive messages from the server."""
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            if msg.startswith("MSG:"):
                update_chat(msg[4:] + "\n", "client")
            elif msg.startswith("FILE:"):
                _, filename, file_size = msg.split(":")
                receive_file(filename, int(file_size))
        except:
            update_chat("❌ Disconnected from server! Attempting to reconnect...\n", "error")
            connect_to_server()
            break

def send_message(event=None):
    """Send a text message to the server."""
    global client_name
    message = message_entry.get().strip()
    
    if not message or not client_socket:
        return
    
    if client_name is None:
        client_name = message
        update_chat(f"🆔 Name set: {client_name}\n", "success")
    else:
        timestamp = time.strftime("[%H:%M:%S] ")
        update_chat(f"{timestamp}You: {message}\n", "self")
        client_socket.send(f"MSG:{timestamp}{client_name}: {message}".encode())

    message_entry.delete(0, tk.END)

def send_file():
    """Send a file to the server using buffered transfer."""
    file_path = filedialog.askopenfilename()
    if not file_path or not client_socket or not client_name:
        return

    try:
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        client_socket.send(f"FILE:{file_name}:{file_size}".encode())

        with open(file_path, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                client_socket.send(chunk)

        update_chat(f"📂 File Sent: {file_name}\n", "success")
    except Exception as e:
        update_chat(f"❌ File Send Failed: {e}\n", "error")

def receive_file(filename, file_size):
    """Receive a file from the server with optimized performance."""
    save_path = filedialog.asksaveasfilename(initialfile=filename)
    if not save_path:
