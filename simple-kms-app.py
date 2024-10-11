import sqlite3
import datetime
import base64
import uvicorn
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import serialization
from fastapi import FastAPI
from pydantic import BaseModel

class PayLoad(BaseModel):
    payload: str

app = FastAPI()

class KeyManagementStore:
    def __init__(self):
        self.db_path = "./edb_kms.db"
        self.create_db()
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def create_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS edb_secret (id TEXT PRIMARY KEY, encryption_key TEXT, encrypted_data TEXT)''')
        conn.commit()
        conn.close()

    def generate_encryption_key(self):
        encryption_key = Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )
        return encryption_key

    def encrypt_string(self, plain_text):
        encryption_key = self.generate_encryption_key()
        cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(encryption_key[:16]))
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plain_text.encode()) + padder.finalize()
        cipher_text = encryptor.update(padded_data) + encryptor.finalize()
        cipher_text = base64.b64encode(cipher_text).decode()

        # Generate ID and store in database
        id = f"EDB{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        encrypted_text = f"{id}{cipher_text}"
        self.store_encrypted_text(id, encryption_key, encrypted_text)

        return encrypted_text

    def decrypt_string(self, encrypted_text):
        # Extract ID and encrypted text
        id = encrypted_text[:17]
        cipher_text = encrypted_text[17:]

        # Retrieve encryption key from database
        encryption_key = self.get_encryption_key(id)

        if encryption_key:
            cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(encryption_key[:16]))
            decryptor = cipher.decryptor()

            cipher_text = base64.b64decode(cipher_text)
            padded_data = decryptor.update(cipher_text) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plain_text = unpadder.update(padded_data) + unpadder.finalize()
            return plain_text.decode()
        else:
            raise ValueError("Encryption key not found for ID: " + id)

    def store_encrypted_text(self, id, encryption_key, encrypted_text):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO edb_secret VALUES (?, ?, ?)", (id, encryption_key, encrypted_text))
        conn.commit()
        conn.close()

    def get_encryption_key(self, id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT encryption_key FROM edb_secret WHERE id = ?", (id,))
        result = c.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            return None

kms = KeyManagementStore()

@app.post("/encrypt")
async def encrypt_string_x(plain_text: PayLoad):
    encrypted_text = kms.encrypt_string(plain_text.payload)
    return encrypted_text

@app.post("/decrypt")
async def decrypt_string_x(encrypted_text: PayLoad):
    decrypted_text = kms.decrypt_string(encrypted_text.payload)
    return decrypted_text

if __name__ == "__main__":
   uvicorn.run("simple-kms-app:app", host="0.0.0.0", port=8000, reload=True)
