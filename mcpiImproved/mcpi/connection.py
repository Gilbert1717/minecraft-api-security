import base64
from email import message
import socket
import select
import sys
import os
from tokenize import Double
from .util import flatten_parameters_to_bytestring
import cryptography.hazmat.primitives.hashes as hashes
import cryptography.hazmat.primitives.serialization as serialization
import cryptography.hazmat.primitives.asymmetric.padding as padding
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from cryptography.hazmat.primitives import hmac

""" @author: Aron Nieminen, Mojang AB"""

class RequestError(Exception):
    pass
class Connection:
    """Connection to a Minecraft Pi game"""
    RequestFailed = "Fail"

    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))
        self.lastSent = ''
        self.do_handshake()
        iv = b'\x00' * 16
        self.cipher = AES.new(self.AES_key, AES.MODE_CTR, initial_value= iv, nonce = b'',counter = None)
       

    def print_byte(self,bytes):
        for b in bytes:
            print(b, end = " ")




    def do_handshake(self):
        self.public_key = self.socket.recv(1500)
        #self.public_key = serialization.load_der_public_key(self.public_key)
        self.public_key = RSA.import_key(self.public_key)

        self.AES_key = os.urandom(16)
        self.MAC_key = os.urandom(16) # might need to increase the key length

        cipher_rsa = PKCS1_OAEP.new(self.public_key,SHA256)
        # ciphertext= self.public_key.encrypt(self.AES_key + self.MAC_key, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(),label=None))
        ciphertext = cipher_rsa.encrypt(self.AES_key + self.MAC_key)
        print('first byte = ' + str(ciphertext[0]))
        print('last byte = ' + str(ciphertext[255]))

        self.socket.send(base64.encodebytes(ciphertext))
        print(len(base64.encodebytes(ciphertext)))
        print(type(base64.encodebytes(ciphertext)))
        print(self.AES_key[0])
        print(self.MAC_key[0])
        return

    def drain(self):
        """Drains the socket of incoming data"""
        while True:
            readable, _, _ = select.select([self.socket], [], [], 0.0)
            if not readable:
                break
            data = self.socket.recv(1500)
            e =  "Drained Data: <%s>\n"%data.strip()
            e += "Last Message: <%s>\n"%self.lastSent.strip()
            sys.stderr.write(e)

    def send(self, f, *data):
        """
        Sends data. Note that a trailing newline '\n' is added here

        The protocol uses CP437 encoding - https://en.wikipedia.org/wiki/Code_page_437
        which is mildly distressing as it can't encode all of Unicode.
        """
        # TODO: test if the code works well
        

        s = b"".join([f, b"(", flatten_parameters_to_bytestring(data), b")", b"\n"])
        print("before: " + str(s))
        
        s = self.cipher.encrypt(s)
        h = hmac.HMAC(self.MAC_key, hashes.SHA256())
        h.update(s)
        h = h.finalize()
        
    
        
        s = base64.encodebytes(s)
        h = base64.encodebytes(h)
        print(len(s))
        print((s))
        print(len(h))
        print((h))
        print("s+hf --------------")
        message = s + h
        print(message)
        print(len(message))

        print('cipher nonce = ' + str(self.cipher.nonce))
        self._send(message)
        # self._send(message)
        # self._send(message)
        # self.socket.send(hf)
        # self._send(s)
        # self._send(hf)


    def _send(self, s):
        """
        The actual socket interaction from self.send, extracted for easier mocking
        and testing
        """
        self.drain()
        self.lastSent = s

        self.socket.sendall(s)

    def receive(self):
        """Receives data. Note that the trailing newline '\n' is trimmed"""
        s = self.socket.makefile("r").readline().rstrip("\n") #TODO move rstrip("\n") until after decryption
        if s == Connection.RequestFailed:
            raise RequestError("%s failed"%self.lastSent.strip())
        
        #TODO verify mac and decrypt ciphertext here
        return s

    def sendReceive(self, *data):
        """Sends and receive data"""
        self.send(*data)
        return self.receive()
