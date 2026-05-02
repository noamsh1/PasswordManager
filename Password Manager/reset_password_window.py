import customtkinter as ctk
from color_palettes import palette_color
from tooltip_window import ToolTip

WINDOW_WIDTH = 440
WINDOW_HEIGHT = 410

class ResetPasswordWindow(ctk.CTkToplevel):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)
        self.configure(fg_color=palette_color("surface"))

        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("btn_auth"))
        self.icon_circle.place(relx=0.5, y=45, anchor="center")
        self.icon_label = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="🔑", fg_color="transparent", text_color=palette_color("surface"), font=("sans", 20))
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self, anchor="center", text="Reset Password", font=("sans", 26, "bold"), text_color=palette_color("text"))
        self.title_label.place(relx=0.5, y=95, anchor="center")

        self.subtitle = ctk.CTkLabel(self, anchor="center", text="Enter a new password for your account", font=("sans", 13), text_color=palette_color("text_dim"))
        self.subtitle.place(relx=0.5, y=125, anchor="center")

        self.password_label = ctk.CTkLabel(self, anchor="w", text="New Password", font=("sans", 13), text_color=palette_color("text_dim"))
        self.password_label.place(x=30, y=160)

        self.password_entry = ctk.CTkEntry(self, width=336, height=38, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text_color=palette_color("placeholder"), font=("sans", 14), show="•", placeholder_text="Enter new password")
        self.password_entry.place(x=30, y=183)
        ToolTip(self.password_entry, "Strong password requirements:\n- At least 8 characters\n- One uppercase letter\n- One lowercase letter\n- One digit\n- One special character")


        self.show_password_button = ctk.CTkButton(self, width=42, height=38, corner_radius=10, fg_color=palette_color("surface2"), hover_color=palette_color("input_border"), text="\uE7B3", font=("Segoe MDL2 Assets", 16), text_color=palette_color("text"), command=lambda : self.show_password(1))
        self.show_password_button.place(x=372, y=183)

        self.password_label_2 = ctk.CTkLabel(self, anchor="w", text="Confirm Password", font=("sans", 13), text_color=palette_color("text_dim"))
        self.password_label_2.place(x=30, y=228)

        self.password_entry_2 = ctk.CTkEntry(self, width=336, height=38, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), placeholder_text="Re-enter Password", text_color=palette_color("text"), font=("sans", 14), show="•")
        self.password_entry_2.place(x=30, y=251)

        self.show_password_button_2 = ctk.CTkButton(self, width=42, height=38, corner_radius=10, fg_color=palette_color("surface2"), hover_color=palette_color("input_border"), text="\uE7B3", font=("Segoe MDL2 Assets", 16), text_color=palette_color("text"), command=lambda : self.show_password(2))
        self.show_password_button_2.place(x=372, y=251)

        self.reset_button = ctk.CTkButton(self, width=380, height=42, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Reset Password", text_color=palette_color("surface"), font=("sans", 14), command=self.call_reset_password)
        self.reset_button.place(x=30, y=310)

        self.error_text = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 13), text_color=palette_color("error"))
        self.error_text.place(relx=0.5, y=370, anchor="center")

        self.grab_set()


    def call_reset_password(self):
        password = self.password_entry.get()
        password2 = self.password_entry_2.get()
        if password != password2:
            self.display_error("Passwords do not match")
        else:
            self.app.call_reset_password(password)

    def show_password(self, num):
        if num == 1:
            self.password_entry.configure(show="")
            self.show_password_button.configure(text="\uED1A", command=lambda: self.hide_password(1))
        elif num == 2:
            self.password_entry_2.configure(show="")
            self.show_password_button_2.configure(text="\uED1A", command=lambda: self.hide_password(2))

    def hide_password(self, num):
        if num == 1:
            self.password_entry.configure(show="•")
            self.show_password_button.configure(text="\uE7B3", command=lambda: self.show_password(1))
        elif num == 2:
            self.password_entry_2.configure(show="•")
            self.show_password_button_2.configure(text="\uE7B3", command=lambda: self.show_password(2))

    def display_error(self, msg):
        self.error_text.configure(text=msg)

    def close_window(self):
        self.destroy()