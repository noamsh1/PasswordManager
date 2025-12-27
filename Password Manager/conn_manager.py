import socket

SERVER_PORT = 5678
MAX_MESSAGE_LENGTH = 1024

class ConnectionManager():
    
    def __init__(self):
        pass
        
    def create_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_msg(self, socket):
        return socket.recv(MAX_MESSAGE_LENGTH).decode()
    
    def send_msg(self, socket, msg):
        socket.send(msg.encode())
