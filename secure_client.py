import socket
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import time

SERVER_HOST = '192.168.50.191'  # Default server IP
PORT = 65432
BUFFER_SIZE = 4096
PASSWORD = "strongpassword"  # Encryption key
client_socket = None
reconnect_attempts = 0  # Track retries

def connect_to_server():
    """Attempt to connect to the server, retrying with limits."""
    global client_socket, reconnect_attempts
    while reconnect_attempts < 5:  # Retry up to 5 times
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, PORT))
            chat_box.insert(tk.END, "✅ Connected to server!\n", "success")
            chat_box.insert(tk.END, "ℹ️ Type your name and send it as your first message.\n", "info")

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

def send_message(event=None):
    """Send a text message to the server (triggered by button or Enter key)."""
    message = message_entry.get().strip()
    if message and client_socket:
        timestamp = time.strftime("[%H:%M:%S] ")
        chat_box.insert(tk.END, f"{timestamp}You: {message}\n", "self")
        client_socket.send(f"MSG:{timestamp}{message}".encode())
        message_entry.delete(0, tk.END)

# GUI Setup
root = tk.Tk()
root.title("Secure Chat Client")
root.geometry("500x500")
root.configure(bg="#f0f0f0")

chat_box = scrolledtext.ScrolledText(root, width=60, height=20, state=tk.NORMAL, wrap=tk.WORD)
chat_box.pack(pady=10, padx=10)
chat_box.tag_config("info", foreground="blue")
chat_box.tag_config("success", foreground="darkgreen")
chat_box.tag_config("error", foreground="red")
chat_box.tag_config("self", foreground="black", font=("Arial", 10, "bold"))
chat_box.tag_config("client", foreground="black")

message_entry = tk.Entry(root, width=50)
message_entry.pack(pady=5)
message_entry.bind("<Return>", send_message)  # Pressing Enter sends message

send_button = tk.Button(root, text="Send", command=send_message, width=20, bg="#4CAF50", fg="white")
send_button.pack(pady=5)

connect_to_server()
root.mainloop()
