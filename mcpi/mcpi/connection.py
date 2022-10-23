import socket
import select
import sys
import os
from .util import flatten_parameters_to_bytestring

""" @author: Aron Nieminen, Mojang AB"""

class RequestError(Exception):
    pass

class Connection:
    """Connection to a Minecraft Pi game"""
    RequestFailed = "Fail"

    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))
        self.lastSent = ""
        # do_handshake(self)

    def do_handshake(self):
        #receive public key
        #generate AES and mac key
        self.AES_key = os.urandom(16)
        self.MAC_key = os.urandom(1)
        #encrypt key and send
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

        s = b"".join([f, b"(", flatten_parameters_to_bytestring(data), b")", b"\n"])
        # TODO encrypt s and append a mac to it
        self._send(s)

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
