import customtkinter as ctk

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400
CODE_LENGTH = 8

class AuthSelectWindow(ctk.CTkToplevel):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Choose second authentication factor", font= ("sans", 40), text_color= "black")
        self.title.place(x= 355, y= 25, anchor= "center")

        self.email_auth_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Authenticate with Email", text_color= "black", border_color= "green", command= self.call_email_login)
        self.email_auth_button.place(x = 200, y = 200, anchor = "center")

    def call_email_login(self):
        email = self.app.get_email()
        self.app.request_login_code(email)
        self.after(10, self.close_window)

    def close_window(self):
        self.destroy()
