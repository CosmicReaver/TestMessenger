import subprocess
import requests
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# 🔹 URLs for hosted files
UPDATER_URL = "https://raw.githubusercontent.com/CosmicReaver/TestMessenger/main/updater.py"
VERSION_URL = "https://raw.githubusercontent.com/CosmicReaver/TestMessenger/main/updater_version.txt"
LOCAL_VERSION_FILE = "updater_version.txt"
UPDATER_SCRIPT = os.path.join(os.getcwd(), "updater.py")

# GUI Updater Class
class UpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Updater")
        self.root.geometry("350x200")
        self.root.resizable(False, False)

        # Title
        tk.Label(root, text="🔄 Updater", font=("Arial", 14, "bold")).pack(pady=10)

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
        self.check_for_update()

    def get_local_version(self):
        """Reads the local version number."""
        if os.path.exists(LOCAL_VERSION_FILE):
            with open(LOCAL_VERSION_FILE, "r") as f:
                return f.read().strip()
        return "0.0.0"

    def check_for_update(self):
        """Checks for updates and enables the update button if needed."""
        try:
            response = requests.get(VERSION_URL, timeout=5)
            response.raise_for_status()
            latest_version = response.text.strip()
            local_version = self.get_local_version()

            if latest_version > local_version:
                self.status_label.config(text=f"🔔 New version available: {latest_version}")
                self.update_button.config(state=tk.NORMAL)
            else:
                self.status_label.config(text="✅ Updater is up to date")
                self.update_button.config(state=tk.DISABLED)

        except requests.RequestException as e:
            self.status_label.config(text="⚠️ Failed to check updates")
            messagebox.showerror("Update Error", f"Could not check for updates.\n{e}")

    def download_update(self):
        """Downloads the update and replaces the old updater script."""
        self.status_label.config(text="Downloading update...")
        self.progress["value"] = 0
        self.root.update()

        try:
            response = requests.get(UPDATER_URL, stream=True, timeout=10)
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0

            with open(UPDATER_SCRIPT, "wb") as f:
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
            messagebox.showinfo("Update Complete", "Updater has been updated. Restarting...")

            # 🚀 Relaunch the updated updater script
            self.relaunch_updater()

        except requests.RequestException as e:
            self.status_label.config(text="⚠️ Update failed!")
            messagebox.showerror("Download Error", f"Could not download the update.\n{e}")

    def relaunch_updater(self):
        """Restarts the updater script using Python."""
        script_path = os.path.abspath(UPDATER_SCRIPT)
        if os.path.exists(script_path):
            self.root.quit()
            subprocess.Popen([sys.executable, script_path], shell=True)  # Restart using Python
        else:
            messagebox.showerror("Launch Error", f"Could not find the updater script:\n{script_path}")

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = UpdaterApp(root)
    root.mainloop()
