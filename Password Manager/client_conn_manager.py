from conn_manager import ConnectionManager, SERVER_PORT

DEFAULT_SERVER_IP = "127.0.0.1"

class ClientConnectionManager(ConnectionManager):

    def __init__(self):
        super(ClientConnectionManager, self).__init__()
        self.socket = self.create_socket()
        
    def connect(self, server_ip):
        self.socket.connect((server_ip, SERVER_PORT))