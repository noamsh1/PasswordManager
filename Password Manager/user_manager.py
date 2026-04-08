import datetime
import json
import os
from pathlib import Path
from user_data import UserData
from site_data import SiteData
from password_handler import PasswordHandler


MAX_FAILED_LOGIN_ATTEMPTS_ALLOWED = 5
FAILED_LOGIN_ATTEMPTS_MINUTES_WINDOW = 1
TIMEOUT_LENGTH_MINUTES = 2

# script_folder_path = Path(__file__).parent
# USER_FOLDER_PATH = fr"{script_folder_path}\user_folder"
# print(USER_FOLDER_PATH)

class UserManager:

    def __init__(self):
        # self.user_dict = self.load_users()
        self.logged_users = {}
        self.user_login_attempts = {}
        self.users_in_timeout = {}


    def is_user_in_timeout(self, username):
        if username in self.users_in_timeout.keys():
            timeout_entry_time = self.users_in_timeout[username]
            current_time = datetime.datetime.now()
            time_diff = current_time - timeout_entry_time
            if time_diff > datetime.timedelta(minutes = TIMEOUT_LENGTH_MINUTES):
                self.users_in_timeout.pop(username)
                return False
            else:
                return True
        else:
            return False

    def register_failed_login_attempt(self, username):
        """registers the time of the failed login attempt of the user and return whether or not the user has exceeded 
        the max ammount of failed attempts allowed in a certain amount of time"""

        current_time = datetime.datetime.now()
        if username not in self.user_login_attempts.keys():
            self.user_login_attempts[username] = [current_time]
            return False
        else:
            attempts_list = self.user_login_attempts[username]
            failed_login_attempts_count = 1
            for i in range(len(attempts_list) - 1, -1, -1):
                login_time = attempts_list[i]
                time_diff = current_time - login_time
                if time_diff > datetime.timedelta(minutes = FAILED_LOGIN_ATTEMPTS_MINUTES_WINDOW):
                    attempts_list.append(current_time)
                    self.user_login_attempts[username] = attempts_list[i + 1::]
                    return False
                else:
                    failed_login_attempts_count += 1
                    if failed_login_attempts_count > MAX_FAILED_LOGIN_ATTEMPTS_ALLOWED:
                        self.users_in_timeout[username] = current_time
                        return True
                    
            self.user_login_attempts[username].append(current_time)
            return False
        
    def successful_login_attempt(self, username):
        if username in self.user_login_attempts.keys():
            self.user_login_attempts.pop(username)

        

    # def save_user(self, user_data):
    #     path = os.path.join(USER_FOLDER_PATH, user_data.username + ".json")
    #     with open(path, "w") as file:
    #         json.dump(user_data.__dict__, file, indent=4)

    # def load_users(self):
    #     dict = {}
    #     if os.path.exists(USER_FOLDER_PATH):
    #         for entry in os.scandir(USER_FOLDER_PATH):
    #             if entry.is_file():
    #                 with open(entry.path, "r") as file:
    #                     data = json.load(file)
    #                     user_data = self.convert_to_user_data(data)
    #                     dict[user_data.username] = user_data
    #     else:
    #         os.makedirs(USER_FOLDER_PATH)
    #     return dict
    
    # def convert_to_user_data(self, data):
    #     username = data["username"]
    #     password = data["password"]
    #     registered_sites = {}
    #     for site in data["registered_sites"]:
    #         site_data = data["registered_sites"][site]
    #         registered_sites[site] = SiteData(site_data["site_url"], site_data["username"], site_data["password"])
    #     return UserData(username, password, registered_sites)

    # def add_user(self, username, password):
    #     user = UserData(username, password)
    #     self.user_dict[username] = user
    #     self.save_user(user)

    # def does_user_exist(self, username):
    #     return username in self.user_dict.keys()
    
    # def is_strong_password(self, password):
    #     return PasswordHandler.is_strong_password(password)
    
    # def register_site(self, username, site_url, site_username):
    #     generated_password = self.user_dict[username].register_site(site_url, site_username)
    #     self.save_user(self.user_dict[username])
    #     return generated_password
    
    # def change_password(self, username, site_url):
    #     generated_password = self.user_dict[username].change_site_password(site_url)
    #     self.save_user(self.user_dict[username])
    #     return generated_password
    