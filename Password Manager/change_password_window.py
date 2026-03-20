import customtkinter as ctk

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400

class ChangePasswordWindow(ctk.CTkToplevel):

    def __init__(self, app, site_url, site_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Change Site Password", font= ("sans", 50), text_color= "black")
        self.title.place(x= 355, y= 40, anchor= "center")

        self.site_url = site_url
        self.site_url_text = ctk.CTkLabel(self, anchor= "center", text= f"Site url: {self.site_url}", font= ("sans", 25), text_color= "black")
        self.site_url_text.place(x= 100, y= 100)      

        self.site_username = site_username
        self.site_username_text = ctk.CTkLabel(self, anchor= "center", text= f"Username for the site: {self.site_username}", font= ("sans", 25), text_color= "black")
        self.site_username_text.place(x= 100, y= 175)

        self.error_text = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 25), text_color= "red")
        self.error_text.place(x= 300, y= 350)

        self.change_password_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Change Password", text_color= "black", border_color= "green", command= self.change_site_password)
        self.change_password_button.place(x = 300, y= 300)

        self.copy_password_checkbox = ctk.CTkCheckBox(self, width = 50, height= 50, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= "Copy password after the change", font= ("sans", 18))
        self.copy_password_checkbox.select()
        self.copy_password_checkbox.place(x= 375, y= 230)

        self.change_preferences_button = ctk.CTkButton(self, width= 200, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Change Password Generation Preferences", text_color= "black", border_color= "green", command= self.call_password_preferences_window)
        self.change_preferences_button.place(x = 100, y = 230)

        self.grab_set()


    def call_password_preferences_window(self):
        self.app.get_preferences_and_initiate_window(self.site_url)


    def change_site_password(self):
        self.app.call_change_site_password(self.site_url)

    def display_error(self, msg):
        self.error_text.configure(text= msg)

    def close_window(self):
        copy_password = self.copy_password_checkbox.get()
        self.destroy()
        return copy_password