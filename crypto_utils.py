from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64

# Generate a secret key from a password
def derive_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password.encode())

# Encrypt data with AES
def encrypt_file(input_file, output_file, password):
    salt = os.urandom(16)  # Generate a new salt
    key = derive_key(password, salt)
    iv = os.urandom(16)  # AES requires a 16-byte IV

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    with open(input_file, "rb") as f:
        plaintext = f.read()
    
    # Pad data to be a multiple of 16 bytes
    pad_length = 16 - (len(plaintext) % 16)
    plaintext += bytes([pad_length] * pad_length)

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    with open(output_file, "wb") as f:
        f.write(salt + iv + ciphertext)  # Store salt, IV, and ciphertext

# Decrypt data with AES
def decrypt_file(input_file, output_file, password):
    with open(input_file, "rb") as f:
        data = f.read()

    salt = data[:16]  # Extract salt
    iv = data[16:32]  # Extract IV
    ciphertext = data[32:]

    key = derive_key(password, salt)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove padding
    pad_length = plaintext[-1]
    plaintext = plaintext[:-pad_length]

    with open(output_file, "wb") as f:
        f.write(plaintext)
