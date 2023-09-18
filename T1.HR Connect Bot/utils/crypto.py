"""Encryption, hashing, and certificate helpers.

The application itself only uses `encrypt` and `decrypt`, which protect values
stored in the Flask session. The remaining helpers are general utilities kept
from the shared C-Square toolkit.
"""

import base64
import hashlib
import random
import secrets
import string
import urllib.parse
import uuid
from datetime import datetime

from Cryptodome import Random
from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from OpenSSL import crypto


class Crypt:
    """AES and RSA helpers with PKCS#7 padding and Base64 encoding."""

    # ------------------------------------------------------------------
    # AES-256 with a key derived from a passphrase
    # ------------------------------------------------------------------
    def encrypt(self, raw, key):
        """Encrypt `raw` with AES-256-CBC and return Base64(iv + ciphertext)."""
        aes_key = hashlib.sha256(key.encode()).digest()
        padded = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(padded.encode())
        return base64.b64encode(iv + encrypted).decode("utf-8")

    def decrypt(self, encrypted, key):
        """Reverse `encrypt` and return the original string."""
        aes_key = hashlib.sha256(key.encode()).digest()
        encrypted = base64.b64decode(encrypted)
        iv = encrypted[:AES.block_size]
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(encrypted[AES.block_size:])).decode("utf-8")

    # ------------------------------------------------------------------
    # AES-128 with an explicit key and IV
    # ------------------------------------------------------------------
    def encrypt_aes128(self, raw, key, iv):
        """Encrypt `raw` with AES-128-CBC using the given key and IV."""
        padded = self._pad(raw)
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
        encrypted = cipher.encrypt(padded.encode())
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt_aes128(self, encrypted, key, iv, encoding="utf-8"):
        """Reverse `encrypt_aes128`."""
        encrypted = base64.b64decode(encrypted)
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
        return self._unpad(cipher.decrypt(encrypted)).decode(encoding)

    # ------------------------------------------------------------------
    # RSA and X.509 certificates
    # ------------------------------------------------------------------
    def rsa_decrypt(self, encrypted, private_key):
        """Decrypt a double Base64-encoded PKCS#1 v1.5 RSA ciphertext."""
        rsa_key = RSA.importKey(private_key)
        cipher = PKCS1_v1_5.new(rsa_key)
        cipher_text = base64.b64decode(encrypted).decode("utf-8")
        cipher_text = base64.b64decode(cipher_text)
        return cipher.decrypt(cipher_text, None)

    def get_public_key_from_x509_der(self, certificate):
        """Return the PEM public key from a Base64 DER certificate."""
        cert = crypto.load_certificate(crypto.FILETYPE_ASN1, base64.b64decode(certificate))
        return crypto.dump_publickey(crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8")

    def get_x509_der_properties(self, certificate):
        """Return the public key, validity window, and subject fields of a certificate."""
        cert = crypto.load_certificate(crypto.FILETYPE_ASN1, base64.b64decode(certificate))
        subject = cert.get_subject()
        return {
            "publicKey": crypto.dump_publickey(crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8"),
            "validFrom": datetime.strptime(cert.get_notBefore().decode("utf-8"), "%Y%m%d%H%M%SZ"),
            "validTill": datetime.strptime(cert.get_notAfter().decode("utf-8"), "%Y%m%d%H%M%SZ"),
            "OU": subject.OU,
            "CN": subject.CN,
            "serialNumber": subject.serialNumber,
        }

    # ------------------------------------------------------------------
    # Random values, hashing, and encoding
    # ------------------------------------------------------------------
    def generate_uid(self):
        """Return a random UUID4 string."""
        return str(uuid.uuid4())

    def get_random_string(self, length):
        """Return a random string of letters, digits, and punctuation."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(random.choice(characters) for _ in range(length))

    def get_random_hash(self):
        """Return a Base64-encoded SHA-256 hash of a random token."""
        digest = hashlib.sha256(secrets.token_hex(16).encode()).digest()
        return base64.b64encode(digest).decode("utf-8")

    def hash_md5(self, raw):
        """Return the hex MD5 digest of `raw`."""
        return hashlib.md5(raw.encode()).hexdigest()

    def url_encode(self, plain_text):
        """Percent-encode `plain_text`, leaving slashes intact."""
        return urllib.parse.quote(plain_text, safe="/")

    # ------------------------------------------------------------------
    # PKCS#7 padding
    # ------------------------------------------------------------------
    def _pad(self, text):
        block_size = AES.block_size
        pad_length = block_size - len(text) % block_size
        return text + pad_length * chr(pad_length)

    def _unpad(self, data):
        return data[:-ord(data[len(data) - 1:])]
