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

def connect_to_server():
    """Attempt to connect to the server, retrying if unavailable, silently."""
    global client_socket
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, PORT))
            chat_box.insert(tk.END, "✅ Connected to server!\n", "success")
            client_socket.send(client_name.encode())
            threading.Thread(target=receive_messages, daemon=True).start()
            break
        except:
            time.sleep(3)  # Retry after 3 seconds silently

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
    message = message_entry.get()
    if message:
        timestamp = time.strftime("[%H:%M:%S] ")
        chat_box.insert(tk.END, f"{timestamp}You: {message}\n", "self")
        client_socket.send(f"MSG:{timestamp}{client_name}: {message}".encode())
        message_entry.delete(0, tk.END)

def send_file():
    """Encrypt and send a file to the server with progress."""
    filename = filedialog.askopenfilename()
    if filename:
        encrypted_file = filename + ".enc"
        encrypt_file(filename, encrypted_file, PASSWORD)
        file_size = os.path.getsize(encrypted_file)
        client_socket.send(f"FILE:{os.path.basename(encrypted_file)}:{file_size}".encode())
        ack = client_socket.recv(1024).decode()
        if ack != "READY":
            chat_box.insert(tk.END, "❌ Server not ready for file transfer.\n", "error")
            return
        progress_win = tk.Toplevel(root)
        progress_win.title("Sending File")
        progress_label = tk.Label(progress_win, text=f"Sending {os.path.basename(filename)}")
        progress_label.pack()
        progress_bar = ttk.Progressbar(progress_win, length=300, mode='determinate')
        progress_bar.pack()
        with open(encrypted_file, "rb") as f:
            remaining = file_size
            while remaining:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                client_socket.sendall(chunk)
                remaining -= len(chunk)
                progress_bar['value'] = ((file_size - remaining) / file_size) * 100
                root.update_idletasks()
        progress_win.destroy()
        chat_box.insert(tk.END, f"✅ File '{filename}' sent successfully.\n", "success")

def update_server_address():
    """Change the server address via GUI and reconnect."""
    global SERVER_HOST
    new_host = simpledialog.askstring("Change Server", "Enter new server IP:")
    if new_host:
        SERVER_HOST = new_host
        chat_box.insert(tk.END, f"🌐 Server changed to {SERVER_HOST}\n", "info")
        connect_to_server()

# GUI Setup
root = tk.Tk()
root.title("Secure Chat Client")
root.geometry("500x500")
root.configure(bg="#f0f0f0")

client_name = simpledialog.askstring("Client Name", "Enter your name:")
if not client_name:
    client_name = "Anonymous"

chat_box = scrolledtext.ScrolledText(root, width=60, height=20, state=tk.NORMAL, wrap=tk.WORD)
chat_box.pack(pady=10, padx=10)
chat_box.tag_config("info", foreground="blue")
chat_box.tag_config("success", foreground="darkgreen")
chat_box.tag_config("error", foreground="red")
chat_box.tag_config("self", foreground="black", font=("Arial", 10, "bold"))
chat_box.tag_config("client", foreground="black")

message_entry = tk.Entry(root, width=50)
message_entry.pack(pady=5)

send_button = tk.Button(root, text="Send", command=send_message, width=20, bg="#4CAF50", fg="white")
send_button.pack(pady=5)

file_button = tk.Button(root, text="Send File", command=send_file, width=20, bg="#2196F3", fg="white")
file_button.pack(pady=5)

change_server_button = tk.Button(root, text="Change Server", command=update_server_address, width=20, bg="#FF9800", fg="white")
change_server_button.pack(pady=5)

# Connect to server automatically
threading.Thread(target=connect_to_server, daemon=True).start()

root.mainloop()
