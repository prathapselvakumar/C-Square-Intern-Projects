class crypt:
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Cipher import PKCS1_OAEP, AES, PKCS1_v1_5
    from Cryptodome import Random
    from cryptography.x509 import load_der_x509_certificate
    from OpenSSL import crypto
    from datetime import datetime
    import random, secrets, string
    
    import uuid, hashlib, base64, urllib

    def encrypt(self, raw, key):
        _key = self.hashlib.sha256(key.encode()).digest()
        raw = self._pad(raw)
        iv = self.Random.new().read(self.AES.block_size)
        cipher = self.AES.new(_key, self.AES.MODE_CBC, iv)
        enc = cipher.encrypt(raw.encode())

        return self.base64.b64encode(iv + enc).decode('utf-8')

    def decrypt(self, enc, key):
        _key = self.hashlib.sha256(key.encode()).digest()
        enc = self.base64.b64decode(enc)
        iv = enc[:self.AES.block_size]
        cipher = self.AES.new(_key, self.AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[self.AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        bs = self.AES.block_size
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def uid(self):
        return str(self.uuid.uuid4())

    def urlEncode(self, plainText):
        return self.urllib.parse.quote(plainText, safe="/")

    def RSADecrypt(self, enc, key):
        key = self.RSA.importKey(key)
        cipher = self.PKCS1_v1_5.new(key)
        cipher_text = self.base64.b64decode(enc).decode("utf-8")
        cipher_text = self.base64.b64decode(cipher_text)
        plain_text = cipher.decrypt(cipher_text, None)

        return plain_text

    def getPublicKeyX509Der(self, cert):
        crtObj = self.crypto.load_certificate(self.crypto.FILETYPE_ASN1, self.base64.b64decode(cert))
        pubKeyObject = crtObj.get_pubkey()
        pubKeyString = self.crypto.dump_publickey(self.crypto.FILETYPE_PEM, pubKeyObject).decode("utf-8")

        return pubKeyString

    def getX509DerProp(self, cert):
        d = {}
        crtObj = self.crypto.load_certificate(self.crypto.FILETYPE_ASN1, self.base64.b64decode(cert))
        
        return {
            'publicKey': self.crypto.dump_publickey(self.crypto.FILETYPE_PEM, crtObj.get_pubkey()).decode("utf-8"),
            'validFrom': self.datetime.strptime(crtObj.get_notBefore().decode("utf-8"), '%Y%m%d%H%M%SZ'),
            'validTill': self.datetime.strptime(crtObj.get_notAfter().decode("utf-8"), '%Y%m%d%H%M%SZ'),
            'OU': crtObj.get_subject().OU,
            'CN': crtObj.get_subject().CN,
            'serialNumber': crtObj.get_subject().serialNumber
        }
        
    def getRandomString(self, length):
        characters = self.string.ascii_letters + self.string.digits + self.string.punctuation
        password = ''.join(self.random.choice(characters) for i in range(length))

        return password

    def encryptAES128(self, raw, key, iv):
        _key = key.encode()
        iv = iv.encode()
        raw = self._pad(raw)
        cipher = self.AES.new(_key, self.AES.MODE_CBC, iv)
        enc = cipher.encrypt(raw.encode())

        return self.base64.b64encode(enc).decode('utf-8')

    def decryptAES128(self, enc, key, iv, encoding="utf-8"):
        enc = self.base64.b64decode(enc)
        key = key.encode()
        iv = iv.encode()
        
        cipher = self.AES.new(key, self.AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc)).decode(encoding)

    def getRandomHash(self):
        randomHash = self.secrets.token_hex(16)
        randomHash = self.hashlib.sha256(randomHash.encode()).digest()
        return self.base64.b64encode(randomHash).decode('utf-8')

    def hashMd5(self, raw):
        return self.hashlib.md5(raw.encode()).hexdigest()
