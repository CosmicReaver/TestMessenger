import requests
import os
import subprocess

URL = "https://github.com/CosmicReaver/TestMessenger/main/secure_client.py"  # Replace with your file URL
FILENAME = "secure_client.py"

def update_client():
    """Download the latest client.py file and replace the old one."""
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()  # Raises an error for 4xx and 5xx status codes

        with open(FILENAME, "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ Client updated successfully!")

    except requests.exceptions.RequestException as e:
        print(f"❌ Update failed: {e}")

def run_client():
    """Run the updated client script."""
    if os.path.exists(FILENAME):
        try:
            subprocess.run(["python", FILENAME])
        except Exception as e:
            print(f"❌ Failed to run client: {e}")

if __name__ == "__main__":
    update_client()
    run_client()