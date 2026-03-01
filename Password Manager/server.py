from server_protocol_handler import ServerProtocolHandler, DATA_DELIMITER
from server_conn_manager import ServerConnectionManager
from user_manager import UserManager
from database import DataBase
from password_handler import PasswordHandler
from email_manager import EmailManager, EMAIL_CODE_EXPIRATION_TIME
import uuid
import datetime

class Server:


    def __init__(self):
        self.conn_manager = ServerConnectionManager()
        self.socket = self.conn_manager.server_socket
        self.protocol_handler = ServerProtocolHandler()
        self.messages_to_send = []
        self.user_manager = UserManager()
        self.db_manager = DataBase()
        self.email_manager = EmailManager()
        self.conn_code = {}

    def run(self):
        print(f"Server is running on private IP {self.conn_manager.get_private_ip()}")
        while True:
            ready_to_read = self.conn_manager.read_from_socket()
            for current_socket in ready_to_read:
                if current_socket is self.socket:
                    self.conn_manager.accept_client_socket(self.socket)
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
        if cmd == self.protocol_handler.client_messages["login_msg"]:
            self.handle_login_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["signup_msg"]:
            self.handle_signup_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["my_email_msg"]:
            self.handle_my_email_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["send_code_msg"]:
            self.handle_send_code_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["code_login_msg"]:
            self.handle_code_login_msg(conn, data)
        elif cmd == self.protocol_handler.client_messages["register_site_msg"]:
            self.handle_register_site_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["registered_sites_msg"]:
            self.handle_registered_sites_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["site_info_msg"]:
            self.handle_site_info_message(conn, data)
        elif cmd == self.protocol_handler.client_messages["change_password_msg"]:
            self.handle_change_password_message(conn, data)


    def handle_login_message(self, conn, data):
        data_list = self.protocol_handler.split_data(data)
        username = data_list[0]
        password = data_list[1]
        if self.db_manager.does_user_exist(username):
            result = self.db_manager.user_login(username, password)
            if result == None:
                self.build_and_queue_message(conn, "incorrect_password_msg", "")
            else:
                self.user_manager.logged_users[conn] = result
                self.build_and_queue_message(conn, "login_ok_msg", "")
        else:
            self.build_and_queue_message(conn, "username_invalid_msg", "")

        # if self.user_manager.does_user_exist(username):
        #     if self.user_manager.user_dict[username].password == password:
        #         self.user_manager.logged_users[conn] = username
        #         self.build_and_queue_message(conn, "login_ok_msg", "")
        #     else:
        #         self.build_and_queue_message(conn, "incorrect_password_msg", "")
        # else:
        #     self.build_and_queue_message(conn, "username_invalid_msg", "")


    def handle_signup_message(self, conn, data):
        data_list = self.protocol_handler.split_data(data)
        username = data_list[0]
        password = data_list[1]
        email = data_list[2]
        phone_number = data_list[3]
        if self.db_manager.does_user_exist(username):
            self.build_and_queue_message(conn, "user_exists_msg", "")
        else:
            if not PasswordHandler.is_strong_password(password):
                self.build_and_queue_message(conn, "weak_password_msg", "")
            else:
                result = self.db_manager.user_signup(username, password, email, phone_number)
                if result == None:
                    self.build_and_queue_message(conn, "user_exists_msg", "")
                else:
                    self.build_and_queue_message(conn, "signup_ok_msg", "")

        # if self.user_manager.does_user_exist(username):
        #     self.build_and_queue_message(conn, "user_exists_msg", "")
        # elif not self.user_manager.is_strong_password(password):
        #     self.build_and_queue_message(conn, "weak_password_msg", "")
        # else:
        #     self.user_manager.add_user(username, password)
        #     self.build_and_queue_message(conn, "signup_ok_msg", "")

    def handle_my_email_msg(self, conn, data):
        try:
            user_email = self.db_manager.get_user_email(data)
            self.build_and_queue_message(conn, "your_email_msg", user_email)
        except TypeError as e:
            self.build_and_queue_message(conn, "no_email_registered_msg", "")

    def handle_send_code_msg(self, conn, data):
        if data != "":
            code, code_creation_time = self.email_manager.send_login_code_gmail(data)
            self.conn_code[conn] = (code, code_creation_time)
            self.build_and_queue_message(conn, "code_sent_msg", "")

    def handle_code_login_msg(self, conn, data):
        sent_code, code_creation_time = self.conn_code[conn]
        current_time = datetime.datetime.now()
        time_diff = current_time - code_creation_time
        if time_diff > datetime.timedelta(seconds = EMAIL_CODE_EXPIRATION_TIME):
            self.build_and_queue_message(conn, "code_expired_msg", "")
        elif sent_code == data:
            self.build_and_queue_message(conn, "code_correct_msg", "")
        else:
            self.build_and_queue_message(conn, "code_incorrect_msg", "")

    def handle_register_site_message(self, conn, data):
        data_list = self.protocol_handler.split_data(data)
        site_url = data_list[0]
        site_username = data_list[1]
        user_id = self.user_manager.logged_users[conn]
        
        if self.db_manager.does_site_exist(user_id, site_url):
            self.build_and_queue_message(conn, "already_registered_msg", "")
        else:
            generated_password = PasswordHandler.generate_password(12)
            self.db_manager.register_site(user_id, site_url, site_username, generated_password)
            self.build_and_queue_message(conn, "registration_ok_msg", generated_password)

        # if site_url in self.user_manager.user_dict[username].registered_sites.keys():
        #     self.build_and_queue_message(conn, "already_registered_msg", "")
        # else:
        #     generated_password = self.user_manager.register_site(username, site_url, site_username)
        #     self.build_and_queue_message(conn, "registration_ok_msg", generated_password)

    def handle_registered_sites_message(self, conn, data):
        user_id = self.user_manager.logged_users[conn]
        # registered_sites_list = self.user_manager.user_dict[username].registered_sites.keys()
        registered_sites_list = self.db_manager.get_registered_sites(user_id)
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
            generated_password = PasswordHandler.generate_password(12)
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