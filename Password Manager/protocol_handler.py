# Protocol Constants

CMD_FIELD_LENGTH = 20	# Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10**LENGTH_FIELD_LENGTH-1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = chr(0)  # Delimiter character in protocol
DATA_DELIMITER = chr(1)  # Delimiter in the data part of the message 

ERROR_RETURN = None

PROTOCOL_SERVER = {
    "signup_ok_msg" : "SIGNUP_OK",
    "user_exists_msg" : "USER_EXISTS",
    "weak_password_msg" : "WEAK_PASSWORD",
    "login_ok_msg" : "LOGIN_OK",
    "username_invalid_msg" : "USERNAME_INVALID",
    "incorrect_password_msg" : "INCORRECT_PASSWORD",
    "preferences_saved_msg" : "PREFERENCES_SAVED",
    "your_preferences_msg" : "YOUR_PREFERENCES",
    "registration_ok_msg" : "REGISTRATION_OK",
    "already_registered_msg" : "ALREADY_REGISTERED",
    "change_ok_msg" : "CHANGE_OK",
    "not_registered_msg" : "NOT_REGISTERED",
    "your_sites_msg" : "YOUR_SITES",
    "info_msg" : "INFO",
    "code_correct_msg" : "CODE_CORRECT",
    "code_incorrect_msg" : "CODE_INCORRECT",
    "code_expired_msg" : "CODE_EXPIRED",
    "code_sent_msg" : "CODE_SENT",
    "your_email_msg" : "YOUR_EMAIL",
    "no_email_registered_msg" : "NO_EMAIL_REGISTERED",
    "voice_verified_msg" : "VOICE_VERIFIED",
    "voice_not_verified_msg" : "VOICE_NOT_VERIFIED"
}

PROTOCOL_CLIENT = {
    "signup_msg" : "SIGNUP",
    "login_msg" : "LOGIN",
    "save_preferences_msg" : "SAVE_PREFERENCES",
    "get_preferences_msg" : "GET_PREFERENCES",
    "register_site_msg" : "REGISTER_SITE",
    "change_password_msg" : "CHANGE_PASSWORD",
    "registered_sites_msg" : "REGISTERED_SITES",
    "site_info_msg" : "SITE_INFO",
    "code_login_msg" : "CODE_LOGIN",
    "send_code_msg" : "SEND_CODE",
    "my_email_msg" : "MY_EMAIL",
    "voice_auth_msg" : "VOICE_AUTH"
}

class ProtocolHandler:

    def __init__(self):
        self.server_messages = PROTOCOL_SERVER
        self.client_messages = PROTOCOL_CLIENT


    def build_message(self, cmd, data):
        full_msg = ""
        cmd_len = len(cmd)
        data_len = len(data)
        if self.check_validation(cmd, data):
            return ERROR_RETURN
        else:
            full_msg += cmd + " " * (CMD_FIELD_LENGTH - cmd_len) + DELIMITER + "0" * (LENGTH_FIELD_LENGTH - len(str(data_len))) + str(data_len) + DELIMITER + data
        return full_msg

    def parse_message(self, data):
        data_list = data.split(DELIMITER)
        if len(data_list) != 3:
            return ERROR_RETURN, ERROR_RETURN
        cmd = data_list[0].replace(" ", "")
        msg_len = data_list[1]
        msg = data_list[2]
        if self.check_validation(cmd, msg):
            return ERROR_RETURN, ERROR_RETURN
        else:	
            return cmd, msg
    
    def check_validation(self):
        return 
    
    def split_data(self, data):
        return data.split(DATA_DELIMITER)
    
# protocolhandler = ProtocolHandler()
# message = protocolhandler.build_message("SIGNUP", f"Noam{DATA_DELIMITER}123")
# print(message)
# cmd, data = protocolhandler.parse_message(message)
# print(cmd)
# print(data)