import socket
import select
from conn_manager import ConnectionManager, SERVER_PORT
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import os
import base64
import uuid
import threading
import time

MAX_MESSAGES_PER_CYCLE = 4
CYCLE_LENGTH = 1

class ServerConnectionManager(ConnectionManager):
    
    def __init__(self):
        super(ServerConnectionManager, self).__init__()
        self.public_pem = None
        self.client_sockets = []
        self.sockets_to_keys = {}
        self.client_message_count = {}
        self.message_count_dict_lock = threading.Lock()
        self.server_socket = self.setup_socket()
        

    def setup_socket(self):
        server_socket = self.create_socket()
        server_socket.bind(("0.0.0.0", SERVER_PORT))
        server_socket.listen()
        self.generate_RSA()
        threading.Thread(target = self.reset_client_message_count_loop).start()
        # print("Server is up and running")
        return server_socket
    

    def read_from_socket(self):
        ready_to_read, ready_to_write, in_error = select.select([self.server_socket] + self.client_sockets, self.client_sockets, [])
        return ready_to_read
    

    def accept_client_socket(self, socket):
        (client_socket, client_address) = socket.accept()
        print("New client joined!", client_address)
        self.client_sockets.append(client_socket)
        self.handshake(client_socket)

    def has_reached_max_messages(self, conn):
        with self.message_count_dict_lock:
            if conn not in self.client_message_count.keys():
                self.client_message_count[conn] = 1
            else:
                self.client_message_count[conn] += 1
            

            return self.client_message_count[conn] >= MAX_MESSAGES_PER_CYCLE

    def reset_client_message_count_loop(self):
        while True:
            with self.message_count_dict_lock:
                self.client_message_count.clear()
            time.sleep(CYCLE_LENGTH)
            

    def close_conn(self, socket):
        socket.close()
        try:
            self.client_sockets.remove(socket)
        except ValueError:
            pass
        print("Connection closed")


    def get_private_ip(self):
        hostname = socket.gethostname()
        private_ip = socket.gethostbyname(hostname)
        return private_ip
    

    def generate_RSA(self):
        private_key = rsa.generate_private_key(public_exponent = 65537, key_size = 4096)
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(encoding = serialization.Encoding.PEM, 
                                                format = serialization.PrivateFormat.PKCS8,
                                                encryption_algorithm = serialization.NoEncryption())

        self.public_pem = public_key.public_bytes(encoding = serialization.Encoding.PEM,
                                             format = serialization.PublicFormat.SubjectPublicKeyInfo)
        
        os.environ["RSA_PRIVATE_KEY"] = base64.b64encode(private_pem).decode("utf-8")


    def load_and_recv_RSA(self):
        b64_string = os.environ.get("RSA_PRIVATE_KEY")
        private_pem = base64.b64decode(b64_string.encode())
        return private_pem
    
    def recv_and_save_AES(self, client_socket):
        encrypted_AES = self.receive_msg(client_socket)
        private_key = serialization.load_pem_private_key(self.load_and_recv_RSA(), None)

        AES_key = private_key.decrypt(encrypted_AES,
                                      padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                      algorithm=hashes.SHA256(),
                                      label=None))
        
        client_key_id = uuid.uuid4().hex
        self.sockets_to_keys[client_socket] = client_key_id
        os.environ[client_key_id] = base64.b64encode(AES_key).decode("utf-8")


    def get_AES_by_client(self, client_socket):
        client_key = self.sockets_to_keys[client_socket]
        AES_base64 = os.environ.get(client_key)
        client_AES = base64.b64decode(AES_base64.encode())
        return client_AES
    

    def handshake(self, client_socket):
        self.send_msg(client_socket, self.public_pem)
        self.recv_and_save_AES(client_socket)


    def encrypt_msg(self, client_socket, msg):
        client_AES = self.get_AES_by_client(client_socket)
        encrypted_msg = self.encrypt_data(msg, client_AES)
        return encrypted_msg

    def decrypt_msg(self, client_socket, msg):
        client_AES = self.get_AES_by_client(client_socket)
        decrypted_msg = self.decrypt_data(msg, client_AES)
        return decrypted_msg