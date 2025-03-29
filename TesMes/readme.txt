 Step 1: Generate an Encryption Key
Open a Python script or terminal.

Install the required library (if not installed):


pip install cryptography
Run the following script to generate a secure encryption key:


from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open("encryption_key.key", "wb") as key_file:
    key_file.write(key)

print("🔑 Encryption key generated and saved as 'encryption_key.key'")
Your key is now stored in encryption_key.key. Keep it safe!

🔹 Step 2: Build updater.exe
Install PyInstaller (if not installed):


pip install pyinstaller
Navigate to the folder containing your updater script (TesMes.py).

Run the following command to create updater.exe:


pyinstaller --onefile --noconsole updater.py
After the process completes, your updater.exe will be inside the dist folder.