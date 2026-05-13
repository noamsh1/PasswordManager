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
from face_recognizer import FaceRecognizer

class Client:

    def __init__(self):
        self.protocol_handler = ClientProtocolHandler()    # ClientProtocolHandler object
        self.conn_manager = ClientConnectionManager()    # ClientConnectionManager object
        self.conn_manager.connect(self.get_server_ip())
        self.ui = UI(self)    # UI object
        self.audio_manager = AudioManager(self)    # AudioManager object
        self.voice_authenticator = VoiceAuthenticator()    # VoiceAuthenticator object
        self.username = ""    # the username of the logged-in user
        self.is_email_verified = False    # whether the user's email has been verified
        self.bin_voice_signature = None    # the user's voice signature as binary data
        self.bin_face_encoding = None    # the user's face encoding as binary data
        self.are_questions_setup = False    # whether the user has set up security questions
        self.chosen_questions_dict = {}    # dictionary of the user's chosen security questions and answers
        self.auth_options = None    # dictionary of the authentication options available to the user
        self.status = Status.NORMAL    # the current status of the client

    def get_server_ip(self):
        """Returns the server IP from the command line arguments, or the default server IP if not provided."""
        if len(sys.argv) > 1:
            return sys.argv[1]
        else:
            return DEFAULT_SERVER_IP

    def run(self):
        """Starts the client UI."""
        self.ui.run()

    def change_status(self, status):
        """Receives a status and sets it as the client's current status."""
        self.status = status

    def can_user_signup(self):
        """Returns True if the user has completed all required signup steps."""
        if self.is_email_verified:
            return True

    def signup(self, username, password, email):
        """Receives username, password and email, and sends a signup request to the server.\n
        Encodes voice signature and face encoding if available, and includes the chosen security questions.\n
        Notifies the UI of the server's response."""
        phone_number = "0" # Placeholder for phone number, not used in current implementation

        self.auth_options = {}
        if self.bin_voice_signature:
            voice_signature = base64.b64encode(self.bin_voice_signature).decode()
            self.auth_options["voice_auth"] = True
        else:
            voice_signature = ""
            self.auth_options["voice_auth"] = False

        if self.bin_face_encoding:
            face_encoding = base64.b64encode(self.bin_face_encoding).decode()
            self.auth_options["face_auth"] = True
        else:
            face_encoding = ""
            self.auth_options["face_auth"] = False
        
        if self.are_questions_setup:
            questions_str = json.dumps(self.chosen_questions_dict)
        else:
            self.ui.display_signup_error("Security questions are not set")
            return
        msg_data = f"{username}{DATA_DELIMITER}{password}{DATA_DELIMITER}{email}{DATA_DELIMITER}{phone_number}{DATA_DELIMITER}{voice_signature}{DATA_DELIMITER}{face_encoding}{DATA_DELIMITER}{questions_str}"
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
        """Receives username and password, and sends a login request to the server.
        Notifies the UI of the server's response."""
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
        elif cmd == self.protocol_handler.server_messages["timeout_msg"]:
            self.ui.display_login_error(f"Too many login attempts. Timeout for {data} minutes")

    def get_security_questions_list(self):
        """Requests the list of security questions from the server and returns it."""
        self.build_and_send_message(self.protocol_handler.client_messages["security_questions_msg"], "")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["security_questions_list_msg"]:
            security_questions_list = data.split(DATA_DELIMITER)
            return security_questions_list
        
    def setup_security_questions(self, chosen_questions_dict):
        """Receives a dictionary of chosen security questions and answers, saves them and notifies the UI."""
        self.chosen_questions_dict = chosen_questions_dict
        self.are_questions_setup = True
        self.ui.questions_setup_successful()

    def get_user_security_questions(self, username):
        """Receives a username and requests the user's security questions from the server.
        Notifies the UI of the server's response."""
        self.build_and_send_message(self.protocol_handler.client_messages["my_security_questions_msg"], username)
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["your_security_questions_msg"]:
            user_security_questions = data.split(DATA_DELIMITER)
            self.username = username
            self.ui.run_security_questions_auth_window(user_security_questions)
        elif cmd == self.protocol_handler.server_messages["username_invalid_msg"]:
            self.ui.display_login_error("Username does not exist")

    def check_security_answers(self, answers):
        """Receives a list of security answers and sends them to the server for verification.
        Notifies the UI of the server's response."""
        answers_str = DATA_DELIMITER.join(answers)
        self.build_and_send_message(self.protocol_handler.client_messages["check_security_answers_msg"], f"{self.username}{DATA_DELIMITER}{answers_str}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["security_answers_correct_msg"]:
            self.ui.security_answers_correct()
        elif cmd == self.protocol_handler.server_messages["security_answers_incorrect_msg"]:
            self.ui.security_answers_incorrect()
        elif cmd == self.protocol_handler.server_messages["timeout_msg"]:
            self.ui.security_answers_timeout(data)

    def reset_password(self, new_password):
        """Receives a new password and sends a password reset request to the server.
        Notifies the UI of the server's response."""
        self.build_and_send_message(self.protocol_handler.client_messages["reset_password_msg"], f"{self.username}{DATA_DELIMITER}{new_password}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["reset_ok_msg"]:
            self.ui.password_reset_successful(self.username)
        elif cmd == self.protocol_handler.server_messages["weak_password_msg"]:
            self.ui.password_reset_unsuccessful()

    def get_auth_options(self):
        """Requests the available authentication options from the server and returns them."""
        self.build_and_send_message(self.protocol_handler.client_messages["get_auth_options_msg"], f"{self.username}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["your_auth_options_msg"]:
            self.auth_options = json.loads(data)
            return self.auth_options

    def code_login(self, code):
        """Receives a one-time code and sends it to the server for verification.\n
        Handles the response differently depending on the client's current status (signing in, logging in, or recovering password)."""
        self.build_and_send_message(self.protocol_handler.client_messages["code_login_msg"], code)
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["code_correct_msg"]:
            self.is_email_verified = True
            if self.status == Status.SIGNING_IN:
                self.ui.signup_code_correct()
            elif self.status == Status.LOGGING_IN or self.status == Status.RECOVERING_PASSWORD:
                self.ui.login_code_correct()
        elif cmd == self.protocol_handler.server_messages["code_incorrect_msg"]:
            self.ui.code_incorrect()
        elif cmd == self.protocol_handler.server_messages["code_expired_msg"]:
            self.ui.code_expired()
        elif cmd == self.protocol_handler.server_messages["timeout_msg"]:
            self.ui.code_login_timeout(data)

    def request_code(self, client_email):
        """Receives an email address and requests the server to send a one-time login code to it.
        Returns True if the code was sent, False otherwise."""
        self.build_and_send_message(self.protocol_handler.client_messages["send_code_msg"], f"{client_email}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["code_sent_msg"]:
            return True
        else:
            return False
        
    def get_email(self, username = ""):
        """Receives a username and requests the user's email from the server. Returns the email or None if not registered.\n
        If no username is provided, uses the logged-in user's username."""
        if username == "":
            username = self.username
        self.build_and_send_message(self.protocol_handler.client_messages["my_email_msg"], f"{username}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["your_email_msg"]:
            return data
        elif cmd == self.protocol_handler.server_messages["no_email_registered_msg"]:
            return None
        
    def is_email_valid(self, email):
        """Receives an email address and returns True if it is a valid deliverable email, False otherwise."""
        try:
            validate_email(email, check_deliverability=True)
            return True
        except EmailNotValidError as e:
            return False
        
    def start_voice_recording(self):
        """Starts recording audio using the audio manager."""
        self.audio_manager.start_recording()

    def stop_voice_recording(self):
        """Stops the audio recording."""
        self.audio_manager.stop_recording()

    def recording_stopped(self):
        """Callback method called by the audio manager when recording has stopped. Notifies the UI."""
        self.ui.recording_stopped()

    def setup_voice_auth(self):
        """Extracts the voice signature from the recorded audio file and sets up voice authentication.\n
        During signup, notifies the UI. Otherwise, sends the voice signature to the server for storage."""
        self.bin_voice_signature = self.voice_authenticator.calc_voice_signature(self.audio_manager.filename)
        if self.bin_voice_signature is not None:
            if self.status == Status.SIGNING_IN:
                self.ui.voice_auth_setup_successful()
            elif self.status == Status.NORMAL:
                voice_signature = base64.b64encode(self.bin_voice_signature).decode()
                self.build_and_send_message(self.protocol_handler.client_messages["setup_voice_auth_msg"], voice_signature)
                cmd, data = self.receive_and_parse_message()
                if cmd == self.protocol_handler.server_messages["voice_auth_set_msg"]:
                    self.auth_options["voice_auth"] = True
                    self.ui.voice_auth_setup_successful()
        else:
            self.ui.signature_extraction_error()
        os.remove(self.audio_manager.filename)

    def voice_auth(self):
        """Extracts the voice signature from the recorded audio file and sends it to the server for voice authentication.
        Notifies the UI of the server's response."""
        self.bin_voice_signature = self.voice_authenticator.calc_voice_signature(self.audio_manager.filename)
        if self.bin_voice_signature is not None:
            voice_signature = base64.b64encode(self.bin_voice_signature).decode()
            self.build_and_send_message(self.protocol_handler.client_messages["voice_auth_msg"], f"{self.username}{DATA_DELIMITER}{voice_signature}")
            cmd, data = self.receive_and_parse_message()
            if cmd == self.protocol_handler.server_messages["voice_verified_msg"]:
                self.ui.voice_auth_successful()
            elif cmd == self.protocol_handler.server_messages["voice_not_verified_msg"]:
                self.ui.voice_auth_unsuccessful()
            elif cmd == self.protocol_handler.server_messages["timeout_msg"]:
                self.ui.voice_auth_timeout(data)
        else:
            self.ui.signature_extraction_error()

    def get_face_encoding(self, rgb_frame):
        """Receives an RGB frame, extracts the face encoding and stores it.\n
        During login or password recovery, proceeds to face recognition immediately.
        Otherwise, notifies the UI whether a face was located."""
        self.bin_face_encoding = FaceRecognizer.get_face_encodings(rgb_frame)
        if self.bin_face_encoding:
            if self.status == Status.LOGGING_IN or self.status == Status.RECOVERING_PASSWORD:
                self.face_recognition()
            else:
                self.ui.face_located()
        else:
            if self.status != Status.LOGGING_IN and self.status != Status.RECOVERING_PASSWORD:
                self.ui.no_face_located()

    def setup_face_recognition(self):
        """Sets up face recognition using the stored face encoding.\n
        During signup, notifies the UI. Otherwise, sends the face encoding to the server for storage."""
        if self.bin_face_encoding:
            if self.status == Status.SIGNING_IN:
                self.ui.face_recognition_setup_successful()
            elif self.status == Status.NORMAL:
                face_encoding_str = base64.b64encode(self.bin_face_encoding).decode()
                self.build_and_send_message(self.protocol_handler.client_messages["setup_face_recognition_msg"], face_encoding_str)
                cmd, data = self.receive_and_parse_message()
                if cmd == self.protocol_handler.server_messages["face_recognition_set_msg"]:
                    self.auth_options["face_auth"] = True
                    self.ui.face_recognition_setup_successful()
        else:
            self.ui.no_face_located()

    def face_recognition(self):
        """Sends the stored face encoding to the server for face recognition verification.
        Notifies the UI of the server's response."""
        if not self.bin_face_encoding:
            return
        else:
            face_encoding_str = base64.b64encode(self.bin_face_encoding).decode()
        self.build_and_send_message(self.protocol_handler.client_messages["check_face_recognition_msg"], f"{self.username}{DATA_DELIMITER}{face_encoding_str}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["face_matches_msg"]:
            self.ui.face_recognition_successful()
        elif cmd == self.protocol_handler.server_messages["face_not_matches_msg"]:
            self.ui.face_recognition_unsuccessful()
            

    def register_site(self, site_url, site_username, password_preferences):
        """Receives a site URL, site username and optional password preferences, and sends a site registration request to the server.
        Notifies the UI of the server's response."""
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
        """Receives a site URL and requests the password preferences for the site from the server. Returns the preferences dictionary."""
        self.build_and_send_message(self.protocol_handler.client_messages["get_preferences_msg"], f"{site_url}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["not_registered_msg"]:
            print("site not registered")
        elif cmd == self.protocol_handler.server_messages["your_preferences_msg"]:
            password_preferences = json.loads(data)
            return password_preferences

    def update_password_preferences(self, site_url, preferences):
        """Receives a site URL and a preferences dictionary, and sends a request to update the password preferences for the site."""
        preferences_json = json.dumps(preferences)
        self.build_and_send_message(self.protocol_handler.client_messages["save_preferences_msg"], f"{site_url}{DATA_DELIMITER}{preferences_json}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["not_registered_msg"]:
            print("site not registered")
        elif cmd == self.protocol_handler.server_messages["preferences_saved_msg"]:
            print(f"Password preferences for {site_url} saved")

    def get_registered_sites(self, get_deleted):
        """Receives a boolean and requests the list of registered sites from the server.\n
        If get_deleted is True, requests the deleted sites. Otherwise, requests the active sites."""
        self.build_and_send_message(self.protocol_handler.client_messages["registered_sites_msg"], f"{get_deleted}")
        cmd, data = self.receive_and_parse_message()
        registered_sites_list = data.split(DATA_DELIMITER) if data != "" else []
        return registered_sites_list

    def get_site_info(self, site_url):
        """Receives a site URL and requests the site's username and password from the server. Returns them as a tuple."""
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
        """Receives a site URL and requests the server to generate a new password for the site. Returns the new password."""
        self.build_and_send_message(self.protocol_handler.client_messages["change_password_msg"], site_url)
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["not_registered_msg"]:
            print("site not registered")
        elif cmd == self.protocol_handler.server_messages["change_ok_msg"]:
            return data
        
    def delete_site(self, site_url):
        """Receives a site URL and sends a request to the server to delete the site.
        Notifies the UI on success."""
        self.build_and_send_message(self.protocol_handler.client_messages["delete_site_msg"], site_url)
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["not_registered_msg"]:
            print("site not registered")
        elif cmd == self.protocol_handler.server_messages["site_deleted_msg"]:
            self.ui.get_registered_sites()

    def recover_site(self, site_url):
        """Receives a site URL and sends a request to the server to recover the previously deleted site.
        Notifies the UI on success."""
        self.build_and_send_message(self.protocol_handler.client_messages["recover_site_msg"], site_url)
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["not_registered_msg"]:
            print("site not registered")
        elif cmd == self.protocol_handler.server_messages["site_recovered_msg"]:
            self.ui.site_recovery_successful()

    def build_and_send_message(self, cmd, data):
        """Receives cmd and data, builds a protocol message, encrypts it and sends it to the server."""
        msg = self.protocol_handler.build_message(cmd, data)
        encrypted_msg = self.conn_manager.encrypt_data(msg, self.conn_manager.get_AES())
        try:
            self.conn_manager.send_msg(self.conn_manager.socket, encrypted_msg)
        except ConnectionResetError as e:
            self.ui.connection_lost()
            return
        

    def receive_and_parse_message(self):
        """Receives an encrypted message from the server, decrypts it and parses it. Returns the cmd and data."""
        try:
            encrypted_msg = self.conn_manager.receive_msg(self.conn_manager.socket)
        except ConnectionResetError as e:
            self.ui.connection_lost()
            return (None, None)
        decrypted_msg = self.conn_manager.decrypt_data(encrypted_msg, self.conn_manager.get_AES())
        cmd, data = self.protocol_handler.parse_message(decrypted_msg)
        return cmd, data

client = Client()
client.run()