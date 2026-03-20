import customtkinter as ctk
import threading

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400

class SignupWindow(ctk.CTkToplevel):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Signup", font= ("sans", 50), text_color= "black")
        self.title.place(x= 355, y= 25, anchor= "center")

        self.username_text = ctk.CTkLabel(self, anchor= "center", text= "Username:", font= ("sans", 25), text_color= "black")
        self.username_text.place(x= 100, y= 100)

        self.username_entry = ctk.CTkEntry(self, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
        self.username_entry.place(x= 250, y= 100)        

        password_text = ctk.CTkLabel(self, anchor= "center", text= "Password:", font= ("sans", 25), text_color= "black")
        password_text.place(x= 100, y= 150)

        self.password_entry = ctk.CTkEntry(self, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20), show= "•")
        self.password_entry.place(x= 250, y= 150)

        self.show_password_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Show Password", text_color= "black", border_color= "green", command= self.show_password)
        self.show_password_button.place(x = 500, y= 140)

        email_text = ctk.CTkLabel(self, anchor= "center", text= "Email:", font= ("sans", 25), text_color= "black")
        email_text.place(x= 100, y= 200)


        self.email_var = ctk.StringVar()
        self.email_var.trace_add("write", self.on_email_entry_changed)
        self.email_entry = ctk.CTkEntry(self, textvariable= self.email_var, width= 300, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
        self.email_entry.place(x= 200, y= 200)
        self.email_debounce_timer = None

        phone_number_text = ctk.CTkLabel(self, anchor= "center", text= "Phone Number:", font= ("sans", 25), text_color= "black")
        phone_number_text.place(x= 100, y= 250)

        self.phone_number_entry = ctk.CTkEntry(self, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
        self.phone_number_entry.place(x= 300, y= 250)

        self.error_text = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 25), text_color= "red")
        self.error_text.place(x= 300, y= 350)

        self.signup_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Signup", text_color= "black", border_color= "green", state = "disabled", command= self.call_signup)
        self.signup_button.place(x = 300, y= 300)

        self.verify_email_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Verify Email", text_color= "black", border_color= "green", state= "disabled", command= self.call_email_verification)
        self.verify_email_button.place(x = 500, y = 300)

        self.add_voice_auth_button= ctk.CTkButton(self, width= 200, height= 50, corner_radius= 5, fg_color= "blue", hover_color= "light blue", text= "Add Voice Authentication", text_color= "black", border_color= "blue", command= self.call_run_voice_recording_window)
        self.add_voice_auth_button.place(x = 100, y = 300)

        self.transient(app.window)
        self.lift()


    def can_signup(self):
        self.signup_button.configure(state = "normal")

    def show_password(self):
        self.password_entry.configure(show= "")
        self.show_password_button.configure(text= "Hide Password", command= self.hide_password)
    
    def hide_password(self):
        self.password_entry.configure(show= "•")
        self.show_password_button.configure(text= "Show Password", command= self.show_password)

    def call_signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()
        phone_number = self.phone_number_entry.get()
        self.app.call_signup(username, password, email, phone_number)

    def on_email_entry_changed(self, *args):
        self.email_entry.configure(border_color = "blue")
        if self.email_debounce_timer:
            self.after_cancel(self.email_debounce_timer)
        self.email_debounce_timer = self.after(500, self.check_email_validity)

    def check_email_validity(self):
        email = self.email_entry.get()
        self.verify_email_button.configure(state = "disabled")
        self.email_entry.configure(border_color = "yellow")
        thread = threading.Thread(target = self.app.call_is_email_valid, args = (email, ))
        thread.start()

    def email_valid(self):
        self.email_entry.configure(border_color = "green")
        self.verify_email_button.configure(state = "normal")

    def email_invalid(self):
        self.email_entry.configure(border_color = "red")

    def call_email_verification(self):
        email = self.email_entry.get()
        self.app.request_login_code(email)

    def email_verified(self):
        self.verify_email_button.configure(state = "disabled")

    def call_run_voice_recording_window(self):
        self.app.run_voice_recording_window()

    def voice_auth_added(self):
        self.add_voice_auth_button.configure(border_color = "green", border_width = 3)

    def display_signup_error(self, msg):
        self.error_text.configure(text= msg)


    def close_window(self):
        self.destroy()