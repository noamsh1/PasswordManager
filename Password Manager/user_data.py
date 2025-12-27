from site_data import SiteData
from password_handler import PasswordHandler

PASSWORD_LENGTH = 12

class UserData:

    def __init__(self, username, password, registered_sites = {}):
        self.username = username
        self.password = password
        self.registered_sites = registered_sites

    def register_site(self, site_url, site_username):
        site_password = PasswordHandler.generate_password(PASSWORD_LENGTH)
        site = SiteData(site_url, site_username, site_password)
        self.registered_sites[site_url] = site
        return site_password
    
    def change_site_password(self, site_url):
        site_password = PasswordHandler.generate_password(PASSWORD_LENGTH)
        self.registered_sites[site_url].change_password(site_password)
        return site_password