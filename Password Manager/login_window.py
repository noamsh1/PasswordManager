import customtkinter as ctk

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400

class LoginWindow(ctk.CTkToplevel):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Login", font= ("sans", 50), text_color= "black")
        self.title.place(x= 355, y= 25, anchor= "center")

        self.username_text = ctk.CTkLabel(self, anchor= "center", text= "Username:", font= ("sans", 25), text_color= "black")
        self.username_text.place(x= 100, y= 100)

        self.username_entry = ctk.CTkEntry(self, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
        self.username_entry.place(x= 250, y= 100)        

        password_text = ctk.CTkLabel(self, anchor= "center", text= "Password:", font= ("sans", 25), text_color= "black")
        password_text.place(x= 100, y= 175)

        self.password_entry = ctk.CTkEntry(self, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20), show= "•")
        self.password_entry.place(x= 250, y= 175)

        self.show_password_button = login_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Show Password", text_color= "black", border_color= "green", command= self.show_password)
        self.show_password_button.place(x = 500, y= 175)

        self.error_text = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 25), text_color= "red")
        self.error_text.place(x= 300, y= 350)

        login_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Login", text_color= "black", border_color= "green", command= self.call_login)
        login_button.place(x = 300, y= 300)

        self.grab_set() 


    def call_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.app.call_login(username, password)

    def show_password(self):
        self.password_entry.configure(show= "")
        self.show_password_button.configure(text= "Hide Password", command= self.hide_password)
    
    def hide_password(self):
        self.password_entry.configure(show= "•")
        self.show_password_button.configure(text= "Show Password", command= self.show_password)


    def display_login_error(self, msg):
        self.error_text.configure(text= msg)


    def close_window(self):
        self.destroy()