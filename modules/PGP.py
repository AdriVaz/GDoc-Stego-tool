
import rsa
import os
import hashlib
import base64

from Crypto.Cipher import AES

class PGP:
    def __init__(self):
        pass

    # Loads a public RSA key from a PEM file for later use
    def addPublicKey(self, publicKeyFile):
        with open(publicKeyFile, "r") as file:
            keydata = file.read()

        self.publicKey = rsa.PublicKey.load_pkcs1(keydata)

    # Loads a private RSA key from a PEM file for later use
    def addPrivateKey(self, privateKeyFile):
        with open(privateKeyFile, "r") as file:
            keydata = file.read()

        self.privateKey = rsa.PrivateKey.load_pkcs1(keydata)
        
    # Encrypts a message using the previously loaded RSA public key
    def encrypt(self, message, mode=AES.MODE_GCM):
        # Check if a RSA public key has been added
        if not self.publicKey:
            print("ERROR: attempting to encrypt without having added a public key first")
            exit()

        # Create some parameters for AES key generation
        salt     = os.urandom(16)
        password = os.urandom(16)

        # Use the Scrypt KDF to get a AES symmetric key from the password
        aesKey = hashlib.scrypt(password, salt=salt, n=2**14, r=8, p=1, dklen=32)

        # Encrypt the AES key with the RSA public key
        aesKeyEncrypted = rsa.encrypt(aesKey, self.publicKey)

        # Initialize AES
        aes = AES.new(aesKey, mode)

        # Encrypt the message with the previously generated AES key
        cipherText, tag = aes.encrypt_and_digest(message)
        
        # Return the encrypted AES text with the encrypted AES key appended
        return cipherText + aes.nonce + tag + aesKeyEncrypted

    # Decrypts a message using the previously loaded RSA private key
    def decrypt(self, message, mode=AES.MODE_GCM):
        # Check if a RSA private key has been added
        if not self.privateKey:
            print("ERROR: attempting to decrypt without having added a private key first")
            exit()

        # Read the encrypted AES key and some other parameters from the back of the message
        aesKeyEncrypted = message [len(message) - 128          : len(message)]
        tag             = message [len(message) - (128 + 16)   : len(message) - 128]
        nonce           = message [len(message) - (128 + 16*2) : len(message) - (128 + 16)]
        cipherText      = message [0                           : len(message) - (128 + 16*2)]

        # Decrypt the AES key with the RSA private key
        aesKey = rsa.decrypt(aesKeyEncrypted, self.privateKey)

        # Initialize AES
        aes = AES.new(aesKey, mode, nonce=nonce)

        # Decrypt the message with the AES key
        plainText = aes.decrypt_and_verify(cipherText, tag)

        return plainText
