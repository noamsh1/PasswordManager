import customtkinter as ctk
import tkinter as tk

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400

class SiteInfoWindow(ctk.CTkToplevel):

    def __init__(self, app, site_username, site_password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.site_username = site_username
        self.site_password = site_password

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Site Info", font= ("sans", 50), text_color= "black")
        self.title.place(x= 355, y= 40, anchor= "center")

        self.site_username_text = ctk.CTkLabel(self, anchor= "center", text= f"Site username: {self.site_username}", font= ("sans", 25), text_color= "black")
        self.site_username_text.place(x= 100, y= 100)

        self.site_password_text = ctk.CTkLabel(self, anchor= "center", text= f"Site password:", font= ("sans", 25), text_color= "black")
        self.site_password_text.place(x= 100, y= 175)

        self.site_password_entry = ctk.CTkEntry(self, width= 200, height= 30, border_color= "white", textvariable= tk.StringVar(self, self.site_password), text_color= "black", font= ("sans", 20), show= "•", state= "disabled")
        self.site_password_entry.place(x= 300, y= 175)

        self.site_password_show_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "blue", hover_color= "light blue", text= "Show password", text_color= "black", border_color= "blue", command= self.show_password)
        self.site_password_show_button.place(x = 500, y = 220)

        self.site_password_hide_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "blue", hover_color= "light blue", text= "Hide password", text_color= "black", border_color= "blue", command= self.hide_password)

        self.copy_password_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "blue", hover_color= "light blue", text= "Copy password", text_color= "black", border_color= "blue", command= self.call_copy_password)
        self.copy_password_button.place(x = 500, y= 170)

        self.password_copied_text = ctk.CTkLabel(self, anchor= "center", text= f"Password copied to clipboard", font= ("sans", 25), text_color= "black")

        self.grab_set() 

    def close_window(self):
        self.destroy()


    def call_copy_password(self):
        self.app.copy_to_clipboard(self.site_password)
        self.password_copied_text.place(x= 355, y= 300, anchor= "center")

    def show_password(self):
        self.site_password_entry.configure(show= "")
        self.site_password_show_button.place_forget()
        self.site_password_hide_button.place(x = 500, y = 220)
    
    def hide_password(self):
        self.site_password_entry.configure(show= "•")
        self.site_password_hide_button.place_forget()
        self.site_password_show_button.place(x= 500, y= 220)