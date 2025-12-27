import json
import os
from pathlib import Path
from user_data import UserData
from site_data import SiteData
from password_handler import PasswordHandler

script_folder_path = Path(__file__).parent
USER_FOLDER_PATH = fr"{script_folder_path}\user_folder"
print(USER_FOLDER_PATH)

class UserManager:

    def __init__(self):
        self.user_dict = self.load_users()
        self.logged_users = {}


    def save_user(self, user_data):
        path = os.path.join(USER_FOLDER_PATH, user_data.username + ".json")
        with open(path, "w") as file:
            json.dump(user_data.__dict__, file, indent=4)

    def load_users(self):
        dict = {}
        if os.path.exists(USER_FOLDER_PATH):
            for entry in os.scandir(USER_FOLDER_PATH):
                if entry.is_file():
                    with open(entry.path, "r") as file:
                        data = json.load(file)
                        user_data = self.convert_to_user_data(data)
                        dict[user_data.username] = user_data
        else:
            os.makedirs(USER_FOLDER_PATH)
        return dict
    
    def convert_to_user_data(self, data):
        username = data["username"]
        password = data["password"]
        registered_sites = {}
        for site in data["registered_sites"]:
            site_data = data["registered_sites"][site]
            registered_sites[site] = SiteData(site_data["site_url"], site_data["username"], site_data["password"])
        return UserData(username, password, registered_sites)

    def add_user(self, username, password):
        user = UserData(username, password)
        self.user_dict[username] = user
        self.save_user(user)

    def does_user_exist(self, username):
        return username in self.user_dict.keys()
    
    def is_strong_password(self, password):
        return PasswordHandler.is_strong_password(password)
    
    def register_site(self, username, site_url, site_username):
        generated_password = self.user_dict[username].register_site(site_url, site_username)
        self.save_user(self.user_dict[username])
        return generated_password
    
    def change_password(self, username, site_url):
        generated_password = self.user_dict[username].change_site_password(site_url)
        self.save_user(self.user_dict[username])
        return generated_password
    