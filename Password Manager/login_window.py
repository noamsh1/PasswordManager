import customtkinter as ctk
from color_palettes import palette_color

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 460

class LoginWindow(ctk.CTkToplevel):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)
        self.configure(fg_color=palette_color("surface"))

        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(x=200, y=50, anchor="center")
        self.icon = ctk.CTkLabel(self.icon_circle, width=0, height=0, anchor="center", text="🔒", fg_color="transparent", text_color=palette_color("surface"), font=("Segoe UI Emoji", 24))
        self.icon.place(relx=0.5, rely=0.5, anchor="center")
        self.title = ctk.CTkLabel(self, anchor="center", text="Login", font=("sans", 44, "bold"), text_color=palette_color("text"))
        self.title.place(x=200, y=110, anchor="center")

        self.username_text = ctk.CTkLabel(self, anchor="w", text="Username", font=("sans", 16), text_color=palette_color("text_dim"))
        self.username_text.place(x=30, y=170)

        self.username_entry = ctk.CTkEntry(self, width=340, height=38, corner_radius=10, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text_color=palette_color("placeholder"), font=("sans", 16), placeholder_text="Enter your username")
        self.username_entry.place(x=30, y=196)

        password_text = ctk.CTkLabel(self, anchor="w", text="Password", font=("sans", 16), text_color=palette_color("text_dim"))
        password_text.place(x=30, y=248)

        self.password_entry = ctk.CTkEntry(self, width=292, height=38, corner_radius=10, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text_color=palette_color("placeholder"), font=("sans", 16), show="•", placeholder_text="Enter your password")
        self.password_entry.place(x=30, y=274)

        self.show_password_button = ctk.CTkButton(self, width=42, height=38, corner_radius=10, fg_color=palette_color("surface2"), hover_color=palette_color("input_border"), text="\uE7B3", font=("Segoe MDL2 Assets", 16), text_color=palette_color("text"), border_color=palette_color("input_border"), command=self.show_password)
        self.show_password_button.place(x=338, y=274)

        login_button = ctk.CTkButton(self, width=340, height=44, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Login", text_color=palette_color("surface"), border_color=palette_color("accent"), command=self.call_login)
        login_button.place(x=30, y=330)

        reset_password_button = ctk.CTkButton(self, width=220, height=28, text="I forgot my password", text_color=palette_color("accent"), fg_color=palette_color("surface"), hover_color=palette_color("surface"), command=self.call_security_questions_window)
        reset_password_button.bind("<Enter>", lambda e: reset_password_button.configure(text_color=palette_color("accent_hover")))
        reset_password_button.bind("<Leave>", lambda e: reset_password_button.configure(text_color=palette_color("accent")))
        reset_password_button.place(x=200, y=390, anchor="center")

        self.error_text = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 16), text_color=palette_color("error"))
        self.error_text.place(x=200, y=420, anchor="center")

        self.grab_set() 


    def call_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        self.app.call_login(username, password)

    def show_password(self):
        self.password_entry.configure(show="")
        self.show_password_button.configure(text="\uED1A", command=self.hide_password)

    def hide_password(self):
        self.password_entry.configure(show="•")
        self.show_password_button.configure(text="\uE7B3", command=self.show_password)

    def call_security_questions_window(self):
        username = self.username_entry.get()
        self.app.call_get_user_security_questions(username)

    def display_login_error(self, msg):
        self.error_text.configure(text= msg)


    def close_window(self):
        self.destroy()