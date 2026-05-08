from server_protocol_handler import ServerProtocolHandler, DATA_DELIMITER
from server_conn_manager import ServerConnectionManager
from user_manager import UserManager, TIMEOUT_LENGTH_MINUTES
from database import DataBase
from password_handler import PasswordHandler, DEFAULT_SETTINGS
from email_manager import EmailManager, EMAIL_CODE_EXPIRATION_TIME
from voice_authenticator import VoiceAuthenticator
from face_recognizer import FaceRecognizer
import datetime
import base64
import json

class Server:


    def __init__(self):
        self.conn_manager = ServerConnectionManager()   # ServerConnectionManager object
        self.socket = self.conn_manager.server_socket   # The server socket
        self.protocol_handler = ServerProtocolHandler()    # ServerProtocolHandler object
        self.messages_to_send = []    # list of scheduled messages to send
        self.user_manager = UserManager()    # UserManager object
        self.db_manager = DataBase()    # DataBase object
        self.email_manager = EmailManager()    # EmailManager object
        self.voice_authenticator = VoiceAuthenticator()    # VoiceAuthenticator object
        self.conn_code = {}    # dictionary of the codes sent to the clients' emails by the clients' socket

    def run(self):
        """Server main loop"""
        print(f"Server is running on private IP {self.conn_manager.get_private_ip()}")
        while True:
            ready_to_read = self.conn_manager.read_from_socket()
            for current_socket in ready_to_read:
                if current_socket is self.socket:
                    self.conn_manager.accept_client_socket(self.socket)
                else:
                    if self.conn_manager.has_reached_max_messages(current_socket):
                        self.conn_manager.close_conn(current_socket)
                    else:
                        print("New data from client")
                        data = ""
                        cmd = ""
                        try:
                            encrypted_msg = self.conn_manager.receive_msg(current_socket)
                            full_msg = self.conn_manager.decrypt_msg(current_socket, encrypted_msg)
                            print(f"[SERVER]" + full_msg)
                            cmd, data = self.protocol_handler.parse_message(full_msg)
                            if cmd is None or data is None:
                                self.conn_manager.close_conn(current_socket)
                        except ConnectionResetError as e:
                            print(e)
                            self.conn_manager.close_conn(current_socket)
                        except BaseException as baseEx:
                            print(baseEx)
                            self.conn_manager.close_conn(current_socket)
                        if cmd == "":
                            self.conn_manager.close_conn(current_socket)
                        else:
                            print((cmd, data))
                            self.handle_client_message(current_socket, cmd, data)
            self.send_messages_to_clients()

    def handle_client_message(self, conn, cmd, data):
        """Receives conn, cmd and data, and calls the right method that handles the cmd."""
        if cmd == self.protocol_handler.client_messages["login_msg"]:
            self.handle_login_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["signup_msg"]:
            self.handle_signup_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["security_questions_msg"]:
            self.handle_security_questions_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["my_security_questions_msg"]:
            self.handle_my_security_questions_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["check_security_answers_msg"]:
            self.handle_check_security_answers_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["reset_password_msg"]:
            self.handle_reset_password_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["get_auth_options_msg"]:
            self.handle_get_auth_options_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["my_email_msg"]:
            self.handle_my_email_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["send_code_msg"]:
            self.handle_send_code_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["code_login_msg"]:
            self.handle_code_login_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["voice_auth_msg"]:
            self.handle_voice_auth_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["check_face_recognition_msg"]:
            self.handle_check_face_recognition_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["setup_voice_auth_msg"]:
            self.handle_setup_voice_auth_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["setup_face_recognition_msg"]:
            self.handle_setup_face_recognition_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["register_site_msg"]:
            self.handle_register_site_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["registered_sites_msg"]:
            self.handle_registered_sites_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["get_preferences_msg"]:
            self.handle_get_preferences_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["save_preferences_msg"]:
            self.handle_save_preferences_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["site_info_msg"]:
            self.handle_site_info_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["change_password_msg"]:
            self.handle_change_password_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["delete_site_msg"]:
            self.handle_delete_site_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["recover_site_msg"]:
            self.handle_recover_site_msg(conn, data)


    def handle_login_message(self, conn, data):
        """Receives conn and data, and handles the client's login attempt.\n
        Sends an answer to the client. Possible Answers:\n
        login_ok, username_invalid, incorrect_password, timeout."""
        data_list = self.protocol_handler.split_data(data)
        username = data_list[0]
        password = data_list[1]
        if self.user_manager.is_user_in_timeout(username):
            self.build_and_queue_message(conn, "timeout_msg", f"{TIMEOUT_LENGTH_MINUTES}")
        else:
            if self.db_manager.does_user_exist(username):
                result = self.db_manager.user_login(username, password)
                if result == None:
                    in_timeout = self.user_manager.register_failed_login_attempt(username)
                    if in_timeout:
                        self.build_and_queue_message(conn, "timeout_msg", f"{TIMEOUT_LENGTH_MINUTES}")
                    else:
                        self.build_and_queue_message(conn, "incorrect_password_msg", "")
                else:
                    self.user_manager.logged_users[conn] = result
                    self.user_manager.successful_login_attempt(username)
                    self.build_and_queue_message(conn, "login_ok_msg", "")
            else:
                in_timeout = self.user_manager.register_failed_login_attempt(username)
                if in_timeout:
                    self.build_and_queue_message(conn, "timeout_msg", f"{TIMEOUT_LENGTH_MINUTES}")
                else:
                    self.build_and_queue_message(conn, "username_invalid_msg", "")


    def handle_signup_message(self, conn, data):
        """Receives conn and data, and handles the client's signup.\n
        If all the needed signup data was received, Saves the user in the database.\n
        Sends an answer to the client. Possible Answers:\n
        signup_ok, user_exists, weak_password."""
        data_list = self.protocol_handler.split_data(data)
        username = data_list[0]
        password = data_list[1]
        email = data_list[2]
        phone_number = data_list[3]
        voice_signature = data_list[4]
        face_encoding = data_list[5]
        questions_dict = json.loads(data_list[6])

        if voice_signature != "":
            bin_voice_signature = base64.b64decode(voice_signature)
        else:
            bin_voice_signature = None

        if face_encoding != "":
            bin_face_encoding = base64.b64decode(face_encoding)
        else:
            bin_face_encoding = None

        if self.db_manager.does_user_exist(username):
            self.build_and_queue_message(conn, "user_exists_msg", "")
        else:
            if not PasswordHandler.is_strong_password(password):
                self.build_and_queue_message(conn, "weak_password_msg", "")
            else:
                result = self.db_manager.user_signup(username, password, email, phone_number, bin_voice_signature, bin_face_encoding, questions_dict)
                if result == None:
                    self.build_and_queue_message(conn, "user_exists_msg", "")
                else:
                    self.build_and_queue_message(conn, "signup_ok_msg", "")


    def handle_security_questions_msg(self, conn, data):
        """Receives conn and data, and sends the user the list of security questions they can answer."""
        security_questions_list = self.db_manager.get_security_questions_list()
        security_questions_str = DATA_DELIMITER.join(security_questions_list)
        self.build_and_queue_message(conn, "security_questions_list_msg", security_questions_str)

    def handle_my_security_questions_msg(self, conn, data):
        """Receives conn and data, and sends the list of the user's security question to the client.
        If the username is invalid, responds with username_invalid instead."""
        if self.db_manager.does_user_exist(data):
            user_questions_list = self.db_manager.get_user_security_questions(data)
            user_questions_str = DATA_DELIMITER.join(user_questions_list)
            self.build_and_queue_message(conn, "your_security_questions_msg", user_questions_str)
        else:
            self.build_and_queue_message(conn, "username_invalid_msg", "")

    def handle_check_security_answers_msg(self, conn, data):
        """Receives conn and data, and handles the request to check their security answers.\n
        Sends an answer to the client. Possible Answers:\n
        security_answers_correct, security_answers_incorrect, timeout"""
        data_list = self.protocol_handler.split_data(data)
        username, *answers_list = data_list
        if self.user_manager.is_user_in_timeout(username):
            self.build_and_queue_message(conn, "timeout_msg", f"{TIMEOUT_LENGTH_MINUTES}")
        else:
            if self.db_manager.check_user_security_answers(username, answers_list):
                self.user_manager.successful_login_attempt(username)
                self.build_and_queue_message(conn, "security_answers_correct_msg", "")
            else: 
                in_timeout = self.user_manager.register_failed_login_attempt(username)
                if in_timeout:
                    self.build_and_queue_message(conn, "timeout_msg", f"{TIMEOUT_LENGTH_MINUTES}")
                else:
                    self.build_and_queue_message(conn, "security_answers_incorrect_msg", "")

    def handle_reset_password_msg(self, conn, data):
        """Receives conn and data, and handles the client's request to reset the their password to the app.\n
        If the received password is strong enough, the server resets the user's password and responds with reset_ok.
        Otherwise, the server responds with weak_password."""
        data_list = self.protocol_handler.split_data(data)
        username = data_list[0]
        new_password = data_list[1]
        if not PasswordHandler.is_strong_password(new_password):
            self.build_and_queue_message(conn, "weak_password_msg", "")
        else:
            user_id = self.db_manager.reset_user_password(username, new_password)
            self.user_manager.logged_users[conn] = user_id
            self.build_and_queue_message(conn, "reset_ok_msg", "")

    def handle_get_auth_options_msg(self, conn, data):
        """Receives conn and data, and sends the client the authentication options available to them."""
        username = data
        auth_options = self.db_manager.get_user_auth_options(username)
        auth_options_str = json.dumps(auth_options)
        self.build_and_queue_message(conn, "your_auth_options_msg", auth_options_str)

    def handle_my_email_msg(self, conn, data):
        """Receives conn and data, and sends the client their registered email address. If no email registered - responds with no_email_registered."""
        try:
            user_email = self.db_manager.get_user_email(data)
            self.build_and_queue_message(conn, "your_email_msg", user_email)
        except TypeError as e:
            self.build_and_queue_message(conn, "no_email_registered_msg", "")

    def handle_send_code_msg(self, conn, data):
        """Receives conn and data, and sends a one-time code to the client's email."""
        if data != "":
            code, code_creation_time = self.email_manager.send_login_code_gmail(data)
            self.conn_code[conn] = (code, code_creation_time)
            self.build_and_queue_message(conn, "code_sent_msg", "")

    def handle_code_login_msg(self, conn, data):
        """Receives conn and data, and handles the client's code login attempt.\n
        Possible responds: code_correct, code_incorrect, code_expired, timeout."""
        sent_code, code_creation_time = self.conn_code[conn]
        current_time = datetime.datetime.now()
        time_diff = current_time - code_creation_time
        username = self.user_manager.logged_users.get(conn, "")
        if self.user_manager.is_user_in_timeout(username):
            self.build_and_queue_message(conn, "timeout_msg", f"{TIMEOUT_LENGTH_MINUTES}")
        else:
            if time_diff > datetime.timedelta(seconds = EMAIL_CODE_EXPIRATION_TIME):
                self.build_and_queue_message(conn, "code_expired_msg", "")
            elif sent_code == data:
                if username != "":
                    self.user_manager.successful_login_attempt(username)
                self.build_and_queue_message(conn, "code_correct_msg", "")
            else:
                if username != "":
                    in_timeout = self.user_manager.register_failed_login_attempt(username)
                    if in_timeout:
                        self.build_and_queue_message(conn, "timeout_msg", f"{TIMEOUT_LENGTH_MINUTES}")
                    else:
                        self.build_and_queue_message(conn, "code_incorrect_msg", "")
                else:
                    self.build_and_queue_message(conn, "code_incorrect_msg", "")


    def handle_voice_auth_msg(self, conn, data):
        """Receives conn and data, and handles the client's voice authentication attempt.\n
        Possible responds: voice_verified, voice_not_verified, timeout."""
        data_list = self.protocol_handler.split_data(data)
        username = data_list[0]
        login_voice_signature = data_list[1]
        bin_login_voice_signature = base64.b64decode(login_voice_signature)
        bin_stored_voice_signature = self.db_manager.get_voice_signature(username)

        if self.user_manager.is_user_in_timeout(username):
            self.build_and_queue_message(conn, "timeout_msg", f"{TIMEOUT_LENGTH_MINUTES}")
        else:
            if self.voice_authenticator.verify_user(bin_stored_voice_signature, bin_login_voice_signature):
                self.user_manager.successful_login_attempt(username)
                self.build_and_queue_message(conn, "voice_verified_msg", "")
            else:
                in_timeout = self.user_manager.register_failed_login_attempt(username)
                if in_timeout:
                    self.build_and_queue_message(conn, "timeout_msg", f"{TIMEOUT_LENGTH_MINUTES}")
                else:
                    self.build_and_queue_message(conn, "voice_not_verified_msg", "")

    def handle_check_face_recognition_msg(self, conn, data):
        """Receives conn and data, and handles the client's face recognition attempt.
        Possible responds: face_matches, face_not_matches"""
        data_list = self.protocol_handler.split_data(data)
        username = data_list[0]
        face_encoding_str = data_list[1]
        bin_face_encoding = base64.b64decode(face_encoding_str)
        bin_stored_face_encoding = self.db_manager.get_face_encoding(username)
        if FaceRecognizer.compare_faces(bin_stored_face_encoding, bin_face_encoding):
            self.build_and_queue_message(conn, "face_matches_msg", "")
        else:
            self.build_and_queue_message(conn, "face_not_matches_msg", "")


    def handle_setup_voice_auth_msg(self, conn, data):
        """Receives conn and data, and sets up voice authentication for the user."""
        user_id = self.user_manager.logged_users[conn]
        bin_voice_signature = base64.b64decode(data)
        self.db_manager.setup_voice_auth(user_id, bin_voice_signature)
        self.build_and_queue_message(conn, "voice_auth_set_msg", "")

    def handle_setup_face_recognition_msg(self, conn, data):
        """Receives conn and data, and sets up face recognition for the user."""
        user_id = self.user_manager.logged_users[conn]
        bin_face_encoding = base64.b64decode(data)
        self.db_manager.setup_face_recognition(user_id, bin_face_encoding)
        self.build_and_queue_message(conn, "face_recognition_set_msg", "")

    def handle_save_preferences_message(self, conn, data):
        data_list = self.protocol_handler.split_data(data)
        site_url = data_list[0]
        preferences_json = data_list[1]
        password_preferences = json.loads(preferences_json)
        user_id = self.user_manager.logged_users[conn]
        if not self.db_manager.does_site_exist(user_id, site_url):
            self.build_and_queue_message(conn, "not_registered_msg", "")
        else:
            self.db_manager.update_password_preferences(user_id, site_url, password_preferences)
            self.build_and_queue_message(conn, "preferences_saved_msg", "")

    def handle_get_preferences_message(self, conn, data):
        user_id = self.user_manager.logged_users[conn]
        if not self.db_manager.does_site_exist(user_id, data):
            self.build_and_queue_message(conn, "not_registered_msg", "")
        else:
            preferences = self.db_manager.get_password_preferences(user_id, data)
            preferences_json = json.dumps(preferences)
            self.build_and_queue_message(conn, "your_preferences_msg", preferences_json)


    def handle_register_site_message(self, conn, data):
        data_list = self.protocol_handler.split_data(data)
        site_url = data_list[0]
        site_username = data_list[1]
        user_id = self.user_manager.logged_users[conn]

        if self.db_manager.does_site_exist(user_id, site_url):
            self.build_and_queue_message(conn, "already_registered_msg", "")
        else:
            if data_list[2] != "":
                password_preferences = json.loads(data_list[2])
                generated_password = PasswordHandler.generate_password(password_preferences)
            else:
                password_preferences = None
                generated_password = PasswordHandler.generate_password(DEFAULT_SETTINGS)
            self.db_manager.register_site(user_id, site_url, site_username, generated_password, password_preferences)
            self.build_and_queue_message(conn, "registration_ok_msg", generated_password)

        # if site_url in self.user_manager.user_dict[username].registered_sites.keys():
        #     self.build_and_queue_message(conn, "already_registered_msg", "")
        # else:
        #     generated_password = self.user_manager.register_site(username, site_url, site_username)
        #     self.build_and_queue_message(conn, "registration_ok_msg", generated_password)

    def handle_registered_sites_message(self, conn, data):
        user_id = self.user_manager.logged_users[conn]
        if data == "True":
            get_deleted_sites = True
        else:
            get_deleted_sites = False
        registered_sites_list = self.db_manager.get_registered_sites(user_id, get_deleted_sites)
        registered_sites_msg = DATA_DELIMITER.join(registered_sites_list)
        self.build_and_queue_message(conn, "your_sites_msg", registered_sites_msg)
        

    def handle_site_info_message(self, conn, data):
        site_url = data
        user_id = self.user_manager.logged_users[conn]

        if self.db_manager.does_site_exist(user_id, site_url):
            site_username, site_password = self.db_manager.get_site_info(user_id, site_url)
            self.build_and_queue_message(conn, "info_msg", f"{site_username}{DATA_DELIMITER}{site_password}")
        else:
            self.build_and_queue_message(conn, "not_registered_msg", "")

        # user_registered_sites = self.user_manager.user_dict[username].registered_sites
        # if site_url not in user_registered_sites.keys():
        #     self.build_and_queue_message(conn, "not_registered_msg", "")
        # else:
        #     site_username = user_registered_sites[site_url]["username"]
        #     site_password = user_registered_sites[site_url]["password"]
        #     self.build_and_queue_message(conn, "info_msg", f"{site_username}{DATA_DELIMITER}{site_password}")

    def handle_change_password_message(self, conn, data):
        site_url = data
        user_id = self.user_manager.logged_users[conn]

        if self.db_manager.does_site_exist(user_id, site_url):
            password_preference = self.db_manager.get_password_preferences(user_id, site_url)
            generated_password = PasswordHandler.generate_password(password_preference)
            self.db_manager.change_site_password(user_id, site_url, generated_password)
            self.build_and_queue_message(conn, "change_ok_msg", generated_password)
        else:
            self.build_and_queue_message(conn, "not_registered_msg", "")
            
        # user_registered_sites = self.user_manager.user_dict[username].registered_sites
        # if site_url not in user_registered_sites.keys():
        #     self.build_and_queue_message(conn, "not_registered_msg", "")
        # else:
        #     generated_password = self.user_manager.change_password(username, site_url)
        #     self.build_and_queue_message(conn, "change_ok_msg", generated_password)


    def handle_delete_site_msg(self, conn, data):
        site_url = data
        user_id = self.user_manager.logged_users[conn]

        if self.db_manager.does_site_exist(user_id, site_url):
            self.db_manager.delete_site(user_id, site_url)
            self.build_and_queue_message(conn, "site_deleted_msg", "")
        else:
            self.build_and_queue_message(conn, "not_registered_msg", "")


    def handle_recover_site_msg(self, conn, data):
        site_url = data
        user_id = self.user_manager.logged_users[conn]

        if self.db_manager.does_deleted_site_exist(user_id, site_url):
            self.db_manager.recover_site(user_id, site_url)
            self.build_and_queue_message(conn, "site_recovered_msg", "")
        else:
            self.build_and_queue_message(conn, "not_registered_msg", "")


    def build_and_queue_message(self, conn, cmd, data):
        msg = self.protocol_handler.build_message(self.protocol_handler.server_messages[cmd], data)
        self.messages_to_send.append((conn, msg))
        

    def send_messages_to_clients(self):
        for conn, msg in self.messages_to_send:
            encrypted_msg = self.conn_manager.encrypt_msg(conn, msg)
            self.conn_manager.send_msg(conn, encrypted_msg)
        self.messages_to_send.clear()

server = Server()
server.run()