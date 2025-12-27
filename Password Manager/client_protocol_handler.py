from protocol_handler import *



class ClientProtocolHandler(ProtocolHandler):
    
    def __init__(self):
        super(ClientProtocolHandler, self).__init__()
        

    def check_validation(self, cmd, data):
        cmd_len = len(cmd)
        data_len = len(data)
        if cmd not in self.client_messages or cmd_len > CMD_FIELD_LENGTH or data_len > MAX_DATA_LENGTH:
            return False
        else:
            return True



