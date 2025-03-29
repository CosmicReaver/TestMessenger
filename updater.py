import requests

URL = "https://github.com/CosmicReaver/TestMessenger/blob/main/secure_client.py"  # Replace with your file URL
FILENAME = "secure_client.py"

# Download latest version
response = requests.get(URL)
if response.status_code == 200:
    with open(FILENAME, "w") as f:
        f.write(response.text)
    print("✅ Client updated!")

# Run the updated client
exec(open(FILENAME).read())
