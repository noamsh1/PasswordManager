import socket
from cryptography.fernet import Fernet

SERVER_PORT = 5678
MAX_MESSAGE_LENGTH = 4096

class ConnectionManager():
    
    def __init__(self):
        pass
        
    def create_socket(self):
        """Method creates a TCP socket object and returns it"""
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_msg(self, socket):
        """Method receives a message from given socket and returns the decoded message"""
        msg = socket.recv(MAX_MESSAGE_LENGTH)
        try:
            decoded_msg = msg.decode()
        except UnicodeDecodeError as e:
            return msg
        else:
            return decoded_msg
    
    def send_msg(self, socket, msg):
        """Method receives a socket and a message, and sends the encoded message to the received socket"""
        if isinstance(msg, str):
            socket.send(msg.encode())
        elif isinstance(msg, bytes):
            socket.send(msg)
        else:
            print("msg couldn't be sent")


    def encrypt_data(self, data, AES_key):
        """Method receives data and an AES key, and returns the encrypted message"""
        encryptor = Fernet(AES_key)
        msg_bytes = data.encode()
        return encryptor.encrypt(msg_bytes)

    def decrypt_data(self, data, AES_key):
        """Method receives data and an AES key, and returns the decrypted data"""
        decryptor = Fernet(AES_key)
        try:
            decrypted_msg = decryptor.decrypt(data).decode()
        except Exception as e:
            print(e)
            print("exeption in decrypt")
            return None
        else:
            return decrypted_msg
