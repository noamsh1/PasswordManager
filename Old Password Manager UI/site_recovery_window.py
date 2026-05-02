import customtkinter as ctk
from CTkListbox import *

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400

class SiteRecoveryWindow(ctk.CTkToplevel):

    def __init__(self, app, deleted_sites, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Recover Site", font= ("sans", 50), text_color= "black")
        self.title.place(x= 355, y= 25, anchor= "center")

        self.deleted_sites_list = CTkListbox(self, height= 200, width= 610, command= self.enable_recover_button)
        if deleted_sites is not None:
            for site_url in deleted_sites:
                self.deleted_sites_list.insert("end", site_url)
        self.deleted_sites_list.place(x= 50, y= 70)

        self.error_text = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 25), text_color= "red")
        self.error_text.place(x= 300, y= 350)

        self.recover_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Recover", text_color= "black", border_color= "green", state= "disabled", command= self.recover_site)
        self.recover_button.place(x = 300, y= 300)

        self.lift()
        self.focus_force()
        self.grab_set()


    def enable_recover_button(self, *args):
        self.recover_button.configure(state= "normal")

    def recover_site(self):
        site_url = self.deleted_sites_list.get()
        self.app.call_recover_site(site_url)

    def display_error(self, msg):
        self.error_text.configure(text= msg)


    def close_window(self):
        self.grab_release()
        self.destroy()