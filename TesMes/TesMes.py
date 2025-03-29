import subprocess
import requests
import os
import tkinter as tk
from tkinter import ttk, messagebox

# 🔹 URLs for hosted files
UPDATE_URL = "https://raw.githubusercontent.com/CosmicReaver/TestMessenger/main/secure_client.py"
VERSION_URL = "https://raw.githubusercontent.com/CosmicReaver/TestMessenger/main/version.txt"
LOCAL_VERSION_FILE = "version.txt"
PYTHON_SCRIPT = os.path.join(os.getcwd(), "secure_client.py")

# GUI Updater Class
class UpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("App Updater")
        self.root.geometry("350x200")
        self.root.resizable(False, False)

        # Title
        tk.Label(root, text="🔄 App Updater", font=("Arial", 14, "bold")).pack(pady=10)

        # Status Label
        self.status_label = tk.Label(root, text="Checking for updates...", font=("Arial", 10))
        self.status_label.pack()

        # Progress Bar
        self.progress = ttk.Progressbar(root, length=300, mode="determinate")
        self.progress.pack(pady=10)

        # Buttons
        self.check_button = tk.Button(root, text="Check for Updates", command=self.check_for_update)
        self.check_button.pack(pady=5)

        self.update_button = tk.Button(root, text="Update Now", command=self.download_update, state=tk.DISABLED)
        self.update_button.pack(pady=5)

        # Auto-check updates on start
        self.checked_for_update = False  # Prevents re-check loops
        self.check_for_update()

    def get_local_version(self):
        """Reads the local version number."""
        if os.path.exists(LOCAL_VERSION_FILE):
            with open(LOCAL_VERSION_FILE, "r") as f:
                return f.read().strip()
        return "0.0.0"

    def check_for_update(self):
        """Checks for updates and enables the update button if needed."""
        if self.checked_for_update:
            return  # Ensures it doesn't loop

        try:
            response = requests.get(VERSION_URL, timeout=5)
            response.raise_for_status()
            latest_version = response.text.strip()
            local_version = self.get_local_version()

            if latest_version > local_version:
                self.status_label.config(text=f"🔔 New version available: {latest_version}")
                self.update_button.config(state=tk.NORMAL)
            else:
                self.status_label.config(text="✅ You have the latest version")
                self.update_button.config(state=tk.DISABLED)
                self.checked_for_update = True  # Prevents looping
                self.root.after(2000, self.launch_application)  # Launch only once after checking

        except requests.RequestException as e:
            self.status_label.config(text="⚠️ Failed to check updates")
            messagebox.showerror("Update Error", f"Could not check for updates.\n{e}")
            self.checked_for_update = True
            self.root.after(2000, self.launch_application)  # Launch only once even on failure

    def download_update(self):
        """Downloads the update, replaces the old file, and auto-launches the app."""
        self.status_label.config(text="Downloading update...")
        self.progress["value"] = 0
        self.root.update()

        try:
            response = requests.get(UPDATE_URL, stream=True, timeout=10)
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0

            with open(PYTHON_SCRIPT, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        self.progress["value"] = (downloaded_size / total_size) * 100
                        self.root.update()

            # Fetch latest version number and update local version file
            latest_version = requests.get(VERSION_URL, timeout=5).text.strip()
            with open(LOCAL_VERSION_FILE, "w") as f:
                f.write(latest_version)

            self.status_label.config(text="✅ Update successful!")
            messagebox.showinfo("Update Complete", "The application has been updated successfully.")

            # 🚀 Auto-launch the updated Python script
            self.launch_application()

        except requests.RequestException as e:
            self.status_label.config(text="⚠️ Update failed!")
            messagebox.showerror("Download Error", f"Could not download the update.\n{e}")
            self.launch_application()

    def launch_application(self):
        """Launches the main Python script and closes the updater."""
        script_path = os.path.abspath(PYTHON_SCRIPT)
        if os.path.exists(script_path):
            self.status_label.config(text="🚀 Launching application...")
            self.root.update()
            try:
                subprocess.Popen(["python", script_path], shell=True)
            except Exception as e:
                messagebox.showerror("Launch Error", f"Could not launch the application.\n{e}")
            self.root.quit()  # Ensure updater closes
        else:
            messagebox.showerror("Launch Error", f"Could not find the application script:\n{script_path}")

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = UpdaterApp(root)
    root.mainloop()
