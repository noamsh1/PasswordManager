import sys
import os
import base64
import json
from client_protocol_handler import ClientProtocolHandler, DATA_DELIMITER
from client_conn_manager import ClientConnectionManager, DEFAULT_SERVER_IP
from ui import UI
from email_validator import validate_email, EmailNotValidError
from client_status import Status
from audio_manager import AudioManager
from voice_authenticator import VoiceAuthenticator

class Client:

    def __init__(self):
        self.protocol_handler = ClientProtocolHandler()
        self.conn_manager = ClientConnectionManager()
        self.conn_manager.connect(self.get_server_ip())
        self.ui = UI(self)
        self.audio_manager = AudioManager(self)
        self.voice_authenticator = VoiceAuthenticator()
        self.username = ""
        self.entered_username = False
        self.entered_password = False
        self.is_email_verified = False
        self.client_email = ""
        self.voice_auth_setup = False
        self.bin_voice_signature = None
        self.status = Status.NORMAL

    def get_server_ip(self):
        if len(sys.argv) > 1:
            return sys.argv[1]
        else:
            return DEFAULT_SERVER_IP

    def run(self):
        self.ui.run()

    def change_status(self, status):
        self.status = status

    def can_user_signup(self):
        if self.is_email_verified:
            return True

    def signup(self, username, password, email, phone_number):
        if self.bin_voice_signature:
            voice_signature = base64.b64encode(self.bin_voice_signature).decode()
        else:
            voice_signature = ""
        print(voice_signature)
        msg_data = f"{username}{DATA_DELIMITER}{password}{DATA_DELIMITER}{email}{DATA_DELIMITER}{phone_number}{DATA_DELIMITER}{voice_signature}"
        self.build_and_send_message(self.protocol_handler.client_messages["signup_msg"], msg_data)
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["user_exists_msg"]:
            self.ui.display_signup_error("Username already exists")
        elif cmd == self.protocol_handler.server_messages["weak_password_msg"]:
            self.ui.display_signup_error("Password is not strong enough")
        elif cmd == self.protocol_handler.server_messages["signup_ok_msg"]:
            print("signup successful")
            self.ui.signup_successful(username, password)


    def login(self, username, password):
        self.build_and_send_message(self.protocol_handler.client_messages["login_msg"], f"{username}{DATA_DELIMITER}{password}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["login_ok_msg"]:
            print("login successful")
            self.username = username
            self.ui.login_succesful(username, password)
        elif cmd == self.protocol_handler.server_messages["username_invalid_msg"]:
            self.ui.display_login_error("Username does not exist")
        elif cmd == self.protocol_handler.server_messages["incorrect_password_msg"]:
            self.ui.display_login_error("Password is incorrect")

    def code_login(self, code):
        self.build_and_send_message(self.protocol_handler.client_messages["code_login_msg"], code)
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["code_correct_msg"]:
            self.is_email_verified = True
            if self.status == Status.SIGNING_IN:
                self.ui.signup_code_correct()
            elif self.status == Status.LOGGING_IN:
                self.ui.login_code_correct()
        elif cmd == self.protocol_handler.server_messages["code_incorrect_msg"]:
            self.ui.code_incorrect()
        elif cmd == self.protocol_handler.server_messages["code_expired_msg"]:
            self.ui.code_expired()

    def request_code(self, client_email):
        self.build_and_send_message(self.protocol_handler.client_messages["send_code_msg"], f"{client_email}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["code_sent_msg"]:
            return True
        else:
            return False
        
    def get_email(self, username = ""):
        if username == "":
            username = self.username
        self.build_and_send_message(self.protocol_handler.client_messages["my_email_msg"], f"{username}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["your_email_msg"]:
            return data
        elif cmd == self.protocol_handler.server_messages["no_email_registered_msg"]:
            return None
        
    def is_email_valid(self, email):
        try:
            validate_email(email, check_deliverability=True)
            return True
        except EmailNotValidError as e:
            return False
        
    def start_voice_recording(self):
        self.audio_manager.start_recording()

    def recording_stopped(self):
        self.ui.recording_stopped()

    def setup_voice_auth(self):
        self.bin_voice_signature = self.voice_authenticator.calc_voice_signature(self.audio_manager.filename)
        if self.bin_voice_signature is not None:
            self.voice_auth_setup = True
            self.ui.voice_auth_setup_successful()
            os.remove(self.audio_manager.filename)
        else:
            self.ui.signature_extraction_error()

    def voice_auth(self):
        self.bin_voice_signature = self.voice_authenticator.calc_voice_signature(self.audio_manager.filename)
        if self.bin_voice_signature is not None:
            voice_signature = base64.b64encode(self.bin_voice_signature).decode()
            self.build_and_send_message(self.protocol_handler.client_messages["voice_auth_msg"], f"{self.username}{DATA_DELIMITER}{voice_signature}")
            cmd, data = self.receive_and_parse_message()
            if cmd == self.protocol_handler.server_messages["voice_verified_msg"]:
                self.ui.voice_auth_successful()
            elif cmd == self.protocol_handler.server_messages["voice_not_verified_msg"]:
                self.ui.voice_auth_unsuccessful()
        else:
            self.ui.signature_extraction_error()


    def register_site(self, site_url, site_username, password_preferences):
        if password_preferences is not None:
            preferences = json.dumps(password_preferences)
        else:
            preferences = ""
        self.build_and_send_message(self.protocol_handler.client_messages["register_site_msg"], f"{site_url}{DATA_DELIMITER}{site_username}{DATA_DELIMITER}{preferences}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["registration_ok_msg"]:
            self.ui.registration_succesful(data)
        elif cmd == self.protocol_handler.server_messages["already_registered_msg"]:
            self.ui.display_registration_error("site already registered")

    def get_password_preferences(self, site_url):
        self.build_and_send_message(self.protocol_handler.client_messages["get_preferences_msg"], f"{site_url}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["not_registered_msg"]:
            print("site not registered")
        elif cmd == self.protocol_handler.server_messages["your_preferences_msg"]:
            password_preferences = json.loads(data)
            return password_preferences

    def update_password_preferences(self, site_url, preferences):
        preferences_json = json.dumps(preferences)
        self.build_and_send_message(self.protocol_handler.client_messages["save_preferences_msg"], f"{site_url}{DATA_DELIMITER}{preferences_json}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["not_registered_msg"]:
            print("site not registered")
        elif cmd == self.protocol_handler.server_messages["preferences_saved_msg"]:
            print(f"Password preferences for {site_url} saved")

    def get_registered_sites(self):
        self.build_and_send_message(self.protocol_handler.client_messages["registered_sites_msg"], "")
        cmd, data = self.receive_and_parse_message()
        registered_sites_list = data.split(DATA_DELIMITER) if data != "" else []
        return registered_sites_list

    def get_site_info(self, site_url):
        self.build_and_send_message(self.protocol_handler.client_messages["site_info_msg"], site_url)
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["not_registered_msg"]:
            print("site not registered")
        elif cmd == self.protocol_handler.server_messages["info_msg"]:
            data_list = data.split(DATA_DELIMITER)
            site_username = data_list[0]
            site_password = data_list[1]
            return site_username, site_password
        
    def change_password(self, site_url):
        self.build_and_send_message(self.protocol_handler.client_messages["change_password_msg"], site_url)
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["not_registered_msg"]:
            print("site not registered")
        elif cmd == self.protocol_handler.server_messages["change_ok_msg"]:
            return data

    def build_and_send_message(self, cmd, data):
        msg = self.protocol_handler.build_message(cmd, data)
        encrypted_msg = self.conn_manager.encrypt_data(msg, self.conn_manager.get_AES())
        self.conn_manager.send_msg(self.conn_manager.socket, encrypted_msg)

    def receive_and_parse_message(self):
        encrypted_msg = self.conn_manager.receive_msg(self.conn_manager.socket)
        decrypted_msg = self.conn_manager.decrypt_data(encrypted_msg, self.conn_manager.get_AES())
        cmd, data = self.protocol_handler.parse_message(decrypted_msg)
        return cmd, data

client = Client()
client.run()