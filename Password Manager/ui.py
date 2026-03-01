import customtkinter as ctk
import threading
from signup_window import SignupWindow
from login_window import LoginWindow
from auth_select_window import AuthSelectWindow
from code_login_window import CodeLoginWindow
from site_registration_window import SiteRegistrationWindow
from site_info_window import SiteInfoWindow
from CTkListbox import *
from client_status import Status

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 675

class UI:

    def __init__(self, client):
        self.window = ctk.CTk()
        self.window.wm_title("Password Manager")
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.resizable(False, False)
        self.client = client

        self.title = ctk.CTkLabel(self.window, anchor= "center", text= "Password Manager", font= ("sans", 50), text_color= "black")
        self.title.place(x= 100, y= 50, anchor= "nw")

        self.login_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Login", text_color= "black", border_color= "green", command= self.run_login_window)
        self.login_button.place(x = 900, y= 50)

        self.login_window = None

        self.signup_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Signup", text_color= "black", border_color= "green", command= self.run_signup_window)
        self.signup_button.place(x= 700, y= 50)

        self.signup_window = None

        self.auth_select_window = None
        self.code_login_window = None

        self.register_site_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Register Site", text_color= "black", border_color= "green", command= self.run_site_registration_window)
        self.username_text = ctk.CTkLabel(self.window, anchor= "center", text= "", font= ("sans", 25), text_color= "black")
        self.site_registration_window = None

        self.registered_sites_list = CTkListbox(self.window, height= 350, width= 1000, command= self.enable_site_buttons)

        self.site_info_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "View site info", text_color= "black", border_color= "green", state= "disabled", command= self.show_selected_site_info)
        self.site_info_window = None

        self.change_password_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Change site password", text_color= "black", border_color= "green", state= "disabled", command= self.call_change_password)

    def run(self):
        self.window.mainloop()

    def run_signup_window(self):
        self.client.change_status(Status.SIGNING_IN)
        if self.signup_window is None or not self.signup_window.winfo_exists():
            self.signup_window = SignupWindow(self)
        else:
            self.signup_window.focus()

    def call_signup(self, username, password, email, phone_number):
        self.client.signup(username, password, email, phone_number)

    def display_signup_error(self, msg):
        self.signup_window.display_signup_error(msg)

    def signup_successful(self, username, password):
        self.signup_window.close_window()
        self.call_login(username, password)

    def run_login_window(self):
        self.client.change_status(Status.LOGGING_IN)
        if self.login_window is None or not self.login_window.winfo_exists():
            self.login_window = LoginWindow(self)
        else:
            self.login_window.focus()
        

    def call_login(self, username, password):
        self.client.login(username, password)

    def display_login_error(self, msg):
        self.login_window.display_login_error(msg)

    def login_succesful(self, username, password):
        if not self.login_window is None:
            self.login_window.close_window()
        self.login_button.place_forget()
        self.signup_button.place_forget()
        if self.client.status == Status.SIGNING_IN:
            self.setup_user(username)
            self.client.change_status(Status.NORMAL)
        elif self.client.status == Status.LOGGING_IN:
            self.run_auth_select_window()


    def get_email(self):
        return self.client.get_email()

    def run_auth_select_window(self):
        if self.auth_select_window is None or not self.auth_select_window.winfo_exists():
            self.auth_select_window = AuthSelectWindow(self)
        else:
            self.auth_select_window.focus()


    def run_code_login_window(self, client_email):
        if self.code_login_window is None or not self.code_login_window.winfo_exists():
            self.code_login_window = CodeLoginWindow(self, client_email)
            self.code_login_window.focus()
            self.code_login_window.lift()
        else:
            self.code_login_window.focus()
            self.code_login_window.lift()

    def request_login_code(self, client_email):
        was_code_sent = self.client.request_code(client_email)
        if was_code_sent:
            self.run_code_login_window(client_email)
    
    def call_is_email_valid(self, email):
        result = self.client.is_email_valid(email)
        if result:
            self.signup_window.email_valid()
        else:
            self.signup_window.email_invalid()

    def call_check_code(self, code):
        self.client.code_login(code)

    def signup_code_correct(self):
        self.code_login_window.close_window()
        if self.client.can_user_signup():
            self.signup_window.can_signup()
            self.signup_window.email_verified()


    def login_code_correct(self):
        self.code_login_window.close_window()
        username = self.client.username
        self.setup_user(username)

    def code_incorrect(self):
        self.code_login_window.incorrect_code_feedback()

    def code_expired(self):
        self.code_login_window.display_code_expired_msg()

    def get_registered_sites(self):
        return self.client.get_registered_sites()

    def setup_user(self, username):
        self.username_text.configure(text= username)
        self.username_text.place(x= 900, y= 75)
        self.register_site_button.place(x= 150, y= 150)
        self.site_info_button.place(x= 350, y= 150)
        self.change_password_button.place(x= 550, y= 150)

        self.load_registered_sites()
        self.registered_sites_list.place(x= 100, y= 250)

    def run_site_registration_window(self):
        if self.site_registration_window is None or not self.site_registration_window.winfo_exists():
            self.site_registration_window = SiteRegistrationWindow(self)
        else:
            self.site_registration_window.focus()

    def call_register_site(self, site_url, site_username):
        self.client.register_site(site_url, site_username)

    def display_registration_error(self, msg):
        self.site_registration_window.display_registration_error(msg)

    def registration_succesful(self, password):
        copy_password = self.site_registration_window.close_window()
        self.load_registered_sites()
        if copy_password:
            self.copy_to_clipboard(password)

    def load_registered_sites(self):
        self.registered_sites_list.delete("all")
        registered_sites = self.get_registered_sites()
        for site_url in registered_sites:
            self.registered_sites_list.insert("end", site_url)

    def enable_site_buttons(self, site):
        self.site_info_button.configure(state= "normal")
        self.change_password_button.configure(state= "normal")


    def show_selected_site_info(self):
        site_url = self.registered_sites_list.get()
        site_username, site_password = self.call_site_info(site_url)
        self.run_site_info_window(site_username, site_password)

    def call_site_info(self, site_url):
        return self.client.get_site_info(site_url)
    
    def run_site_info_window(self, site_username, site_password):
        if self.site_info_window is None or not self.site_info_window.winfo_exists():
            self.site_info_window = SiteInfoWindow(self, site_username, site_password)
        else:
            self.site_info_window.focus()

    def call_change_password(self):
        site_url = self.registered_sites_list.get()
        generated_password = self.client.change_password(site_url)
        self.copy_to_clipboard(generated_password)

    def copy_to_clipboard(self, text):
        self.window.clipboard_clear()
        self.window.clipboard_append(text) 
        self.window.update()