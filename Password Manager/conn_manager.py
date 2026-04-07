import socket
from cryptography.fernet import Fernet

SERVER_PORT = 5678
MAX_MESSAGE_LENGTH = 4096

class ConnectionManager():
    
    def __init__(self):
        pass
        
    def create_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_msg(self, socket):
        msg = socket.recv(MAX_MESSAGE_LENGTH)
        try:
            decoded_msg = msg.decode()
        except UnicodeDecodeError as e:
            return msg
        else:
            return decoded_msg
    
    def send_msg(self, socket, msg):
        if isinstance(msg, str):
            socket.send(msg.encode())
        elif isinstance(msg, bytes):
            socket.send(msg)
        else:
            print("msg couldn't be sent")


    def encrypt_data(self, data, AES_key):
        encryptor = Fernet(AES_key)
        msg_bytes = data.encode()
        return encryptor.encrypt(msg_bytes)

    def decrypt_data(self, data, AES_key):
        decryptor = Fernet(AES_key)
        try:
            decrypted_msg = decryptor.decrypt(data).decode()
        except Exception as e:
            print(e)
            print("exeption in decrypt")
            return None
        else:
            return decrypted_msg
