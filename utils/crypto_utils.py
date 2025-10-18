import os
import base64
from cryptography.fernet import Fernet

CRYPTO_KEY = os.getenv("CRYPTO_KEY")

if not CRYPTO_KEY:
    raise ValueError("CRYPTO_KEY não configurada no .env")

try:
    key_bytes = CRYPTO_KEY.encode()
    base64.urlsafe_b64decode(key_bytes)
except Exception:
    raise ValueError(
        "CRYPTO_KEY inválida: precisa ser 32 url-safe base64-encoded bytes"
    )

cipher = Fernet(CRYPTO_KEY.encode())


def criptografar_cpf(cpf):
    if not cpf:
        return None
    return cipher.encrypt(cpf.encode()).decode()


def descriptografar_cpf(cpf_criptografado):
    if not cpf_criptografado:
        return None
    return cipher.decrypt(cpf_criptografado.encode()).decode()
