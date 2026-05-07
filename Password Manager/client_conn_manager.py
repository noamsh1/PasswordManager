from conn_manager import ConnectionManager, SERVER_PORT
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import os
import base64

DEFAULT_SERVER_IP = "127.0.0.1"

class ClientConnectionManager(ConnectionManager):

    def __init__(self):
        super(ClientConnectionManager, self).__init__()
        self.socket = self.create_socket()  # the socket of the client
        
    def connect(self, server_ip):
        """Receives the server's ip and connects the client socket to it"""
        self.socket.connect((server_ip, SERVER_PORT))
        self.handshake()

    def generate_and_send_AES(self):
        """Generates an AES key, encrypts it using the server's public RSA key, and sends it to the server."""
        AES_key = Fernet.generate_key()
        os.environ["AES_KEY"] = base64.b64encode(AES_key).decode("utf-8")
        AES_msg = self.public_RSA_key.encrypt(AES_key, 
                                              padding.OAEP(mgf= padding.MGF1(algorithm= hashes.SHA256()),
                                                                            algorithm= hashes.SHA256(),
                                                                            label= None))
        self.send_msg(self.socket, AES_msg)

    def recv_RSA(self):
        """Receives the public RSA key from the server"""
        public_RSA_pem = self.receive_msg(self.socket)
        self.public_RSA_key = serialization.load_pem_public_key(public_RSA_pem.encode())

    def get_AES(self):
        """Get the AES key from the environment variables"""
        b64_string = os.environ.get("AES_KEY")
        AES_key = base64.b64decode(b64_string.encode())
        return AES_key

    def handshake(self):
        """Continues the key exchange process with the server"""
        self.recv_RSA()
        self.generate_and_send_AES()


    