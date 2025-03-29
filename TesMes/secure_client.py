import socket
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import time

SERVER_HOST = '192.168.50.191'  # Default server IP
PORT = 65432
BUFFER_SIZE = 4096
client_socket = None
client_name = None
reconnect_attempts = 0  # Track retries

def connect_to_server():
    """Attempt to connect to the server, retrying with limits."""
    global client_socket, reconnect_attempts
    while reconnect_attempts < 5:  # Retry up to 5 times
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, PORT))
            chat_box.insert(tk.END, "✅ Connected to server!\n", "success")
            chat_box.insert(tk.END, "📢 Type your NAME as the first message!\n", "info")

            threading.Thread(target=receive_messages, daemon=True).start()
            reconnect_attempts = 0  # Reset on success
            return
        except Exception:
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
    """Send a text message to the server."""
    global client_name
    message = message_entry.get().strip()
    
    if not message or not client_socket:
        return
    
    if client_name is None:
        # First message should be the name
        client_name = message
        chat_box.insert(tk.END, f"🆔 Name set: {client_name}\n", "success")
    else:
        # Normal message sending
        timestamp = time.strftime("[%H:%M:%S] ")
        chat_box.insert(tk.END, f"{timestamp}You: {message}\n", "self")
        client_socket.send(f"MSG:{timestamp}{client_name}: {message}".encode())

    message_entry.delete(0, tk.END)

def send_file():
    """Send a file to the server."""
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

        chat_box.insert(tk.END, f"📂 File Sent: {file_name}\n", "success")
    except Exception as e:
        chat_box.insert(tk.END, f"❌ File Send Failed: {e}\n", "error")

def receive_file(filename, file_size):
    """Receive a file from the server."""
    save_path = filedialog.asksaveasfilename(initialfile=filename)
    if not save_path:
        return

    try:
        with open(save_path, "wb") as f:
            received_size = 0
            while received_size < file_size:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
                received_size += len(data)

        chat_box.insert(tk.END, f"📥 File Received: {filename}\n", "success")
    except Exception as e:
        chat_box.insert(tk.END, f"❌ File Receive Failed: {e}\n", "error")

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

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

send_button = tk.Button(button_frame, text="Send", command=send_message, width=15, bg="#4CAF50", fg="white")
send_button.grid(row=0, column=0, padx=5)

file_button = tk.Button(button_frame, text="Send File", command=send_file, width=15, bg="#2196F3", fg="white")
file_button.grid(row=0, column=1, padx=5)

connect_to_server()
root.mainloop()
