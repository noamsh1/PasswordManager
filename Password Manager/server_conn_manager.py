import socket
import select
from conn_manager import ConnectionManager, SERVER_PORT


class ServerConnectionManager(ConnectionManager):
    
    def __init__(self):
        super(ServerConnectionManager, self).__init__()
        self.server_socket = self.setup_socket()
        self.client_sockets = []
        

    def setup_socket(self):
        server_socket = self.create_socket()
        server_socket.bind(("0.0.0.0", SERVER_PORT))
        server_socket.listen()
        # print("Server is up and running")
        return server_socket
    

    def read_from_socket(self):
        ready_to_read, ready_to_write, in_error = select.select([self.server_socket] + self.client_sockets, self.client_sockets, [])
        return ready_to_read
    

    def accept_client_socket(self, socket):
        (client_socket, client_address) = socket.accept()
        print("New client joined!", client_address)
        self.client_sockets.append(client_socket)


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