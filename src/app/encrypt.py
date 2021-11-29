"""
The encryption module encrypts our cassandra database to add a layer of security.
We will convert this encryption module into a pipeline that we can run anytime.
"""

import os
import pathlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")

def generate_key():
    """
    generate it once and save to os.environ
    """
    return Fernet.generate_key().decode("UTF-8")

def encrypt_dir(input_dir, output_dir):
    
    key = ENCRYPTION_KEY
    if not key:
        raise Exception("Encryption key not found")
    
    fer = Fernet(key)
    input_dir = pathlib.Path(input_dir)
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    for path in input_dir.glob("*"):
        _path_bytes = path.read_bytes()
        data = fer.encrypt(_path_bytes)
        relative_path = path.relative_to(input_dir)
        dest_path = output_dir / relative_path
        dest_path.write_bytes(data)


def decrypt_dir(input_dir, output_dir):
    
    key = ENCRYPTION_KEY
    if not key:
        raise Exception("Encryption key not found")
    
    fer = Fernet(key)
    input_dir = pathlib.Path(input_dir)
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    for path in input_dir.glob("*"):
        _path_bytes = path.read_bytes()
        data = fer.decrypt(_path_bytes)
        relative_path = path.relative_to(input_dir)
        dest_path = output_dir / relative_path
        dest_path.write_bytes(data)


# BASE_DIR = pathlib.Path().resolve().parent
# APP_DIR = BASE_DIR / "app"
# IGNORED_DIR = APP_DIR / "ignored"
# ENCRYPTED_DIR = APP_DIR / "encrypted"
# DECRYPTED_DIR = APP_DIR / "decrypted"
