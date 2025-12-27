import sys
from client_protocol_handler import ClientProtocolHandler, DATA_DELIMITER
from client_conn_manager import ClientConnectionManager, DEFAULT_SERVER_IP
from ui import UI

class Client:

    def __init__(self):
        self.protocol_handler = ClientProtocolHandler()
        self.conn_manager = ClientConnectionManager()
        self.conn_manager.connect(self.get_server_ip())
        self.ui = UI(self)

    def get_server_ip(self):
        if len(sys.argv) > 1:
            return sys.argv[1]
        else:
            return DEFAULT_SERVER_IP

    def run(self):
        self.ui.run()

    def signup(self, username, password):
        self.build_and_send_message(self.protocol_handler.client_messages["signup_msg"], f"{username}{DATA_DELIMITER}{password}")
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
            self.ui.login_succesful(username)
        elif cmd == self.protocol_handler.server_messages["username_invalid_msg"]:
            self.ui.display_login_error("Username does not exist")
        elif cmd == self.protocol_handler.server_messages["incorrect_password_msg"]:
            self.ui.display_login_error("Password is incorrect")

    def register_site(self, site_url, site_username):
        self.build_and_send_message(self.protocol_handler.client_messages["register_site_msg"], f"{site_url}{DATA_DELIMITER}{site_username}")
        cmd, data = self.receive_and_parse_message()
        if cmd == self.protocol_handler.server_messages["registration_ok_msg"]:
            self.ui.registration_succesful(data)
            print(f"registration succesful. Password: {data}")
        elif cmd == self.protocol_handler.server_messages["already_registered_msg"]:
            self.ui.display_registration_error("site already registered")

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
            print(f"Site password updated. New password: {data}")

    def build_and_send_message(self, cmd, data):
        msg = self.protocol_handler.build_message(cmd, data)
        self.conn_manager.send_msg(self.conn_manager.socket, msg)

    def receive_and_parse_message(self):
        msg = self.conn_manager.receive_msg(self.conn_manager.socket)
        cmd, data = self.protocol_handler.parse_message(msg)
        return cmd, data

client = Client()
client.run()