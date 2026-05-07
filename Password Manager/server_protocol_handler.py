from protocol_handler import *


class ServerProtocolHandler(ProtocolHandler):

    def __init__(self):
        super(ServerProtocolHandler, self).__init__()

    def check_validation(self, cmd, data):
        """Method receives cmd and data and checks their validation according to server's protocol"""
        print(cmd, data)
        cmd_len = len(cmd)
        data_len = len(data)
        if cmd not in self.client_messages.values() or cmd_len > CMD_FIELD_LENGTH or data_len > MAX_DATA_LENGTH:
            return False
        else:
            return True
        
