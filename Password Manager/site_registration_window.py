import customtkinter as ctk

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400

class SiteRegistrationWindow(ctk.CTkToplevel):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Register Site", font= ("sans", 50), text_color= "black")
        self.title.place(x= 355, y= 40, anchor= "center")

        self.site_url_text = ctk.CTkLabel(self, anchor= "center", text= "Site url:", font= ("sans", 25), text_color= "black")
        self.site_url_text.place(x= 100, y= 100)

        self.site_url_entry = ctk.CTkEntry(self, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
        self.site_url_entry.place(x= 200, y= 100)        

        self.site_username_text = ctk.CTkLabel(self, anchor= "center", text= "Username for the site:", font= ("sans", 25), text_color= "black")
        self.site_username_text.place(x= 100, y= 175)

        self.site_username_entry = ctk.CTkEntry(self, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
        self.site_username_entry.place(x= 360, y= 175)

        self.error_text = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 25), text_color= "red")
        self.error_text.place(x= 300, y= 350, anchor= "center")

        self.register_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Register", text_color= "black", border_color= "green", command= self.call_register_site)
        self.register_button.place(x = 300, y= 300)

        self.copy_password_checkbox = ctk.CTkCheckBox(self, width = 50, height= 50, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= "Copy password after registration", font= ("sans", 18))
        self.copy_password_checkbox.select()
        self.copy_password_checkbox.place(x= 375, y= 230)

        self.preferences = None

        self.change_preferences_button = ctk.CTkButton(self, width= 200, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Change Password Generation Preferences", text_color= "black", border_color= "green", command= self.call_password_preferences_window)
        self.change_preferences_button.place(x = 100, y = 230)

        self.grab_set()


    def call_password_preferences_window(self):
        self.app.run_password_preferences_window(self.preferences)


    def call_register_site(self):
        site_url = self.site_url_entry.get()
        if site_url == "":
            self.display_registration_error("You must enter a site url before registration")
            return
        site_username = self.site_username_entry.get()
        if site_username == "":
            self.display_registration_error("You must enter a username before registration")
            return
        self.app.call_register_site(site_url, site_username, self.preferences)

    def display_registration_error(self, msg):
        self.error_text.configure(text= msg)

    def close_window(self):
        copy_password = self.copy_password_checkbox.get()
        self.destroy()
        return copy_password