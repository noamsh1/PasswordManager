

class SiteData(dict):

    def __init__(self, site_url, username, password):
        # self.site_url = site_url
        # self.username = username
        # self.password = password
        dict.__init__(self, site_url = site_url, username = username, password = password)

    def change_password(self, password):
        self["password"] = password

