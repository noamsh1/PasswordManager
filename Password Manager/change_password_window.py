import customtkinter as ctk
from color_palettes import palette_color

WINDOW_WIDTH = 440
WINDOW_HEIGHT = 420

class ChangePasswordWindow(ctk.CTkToplevel):

    def __init__(self, app, site_url, site_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app    # Reference to the UI instance
        self.site_url = site_url    # URL of the site to change the password for
        self.site_username = site_username    # Username associated with the site

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")
        self.configure(fg_color=palette_color("surface"))

        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=45, anchor="center")
        self.icon = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="🔑", fg_color="transparent", text_color=palette_color("surface"), font=("sans", 20))
        self.icon.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self, anchor="center", text="Change Site Password", font=("sans", 26, "bold"), text_color=palette_color("text"))
        self.title_label.place(relx=0.5, y=95, anchor="center")

        self.section_label = ctk.CTkLabel(self, anchor="w", text="SITE DETAILS", font=("sans", 11, "bold"), text_color=palette_color("accent"))
        self.section_label.place(x=30, y=130)
        self.divider = ctk.CTkFrame(self, width=380, height=2, fg_color=palette_color("divider"))
        self.divider.place(x=30, y=150)

        self.site_url_label = ctk.CTkLabel(self, anchor="w", text="Site URL", font=("sans", 13), text_color=palette_color("text_dim"))
        self.site_url_label.place(x=30, y=160)
        self.site_url_value = ctk.CTkLabel(self, anchor="w", text=self.site_url, font=("sans", 15), text_color=palette_color("text"))
        self.site_url_value.place(x=30, y=183)

        self.site_username_label = ctk.CTkLabel(self, anchor="w", text="Username", font=("sans", 13), text_color=palette_color("text_dim"))
        self.site_username_label.place(x=30, y=218)
        self.site_username_value = ctk.CTkLabel(self, anchor="w", text=self.site_username, font=("sans", 15), text_color=palette_color("text"))
        self.site_username_value.place(x=30, y=241)

        self.copy_password_checkbox = ctk.CTkCheckBox(self, width=20, height=20, corner_radius=4, border_color=palette_color("input_border"), fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), checkmark_color=palette_color("surface"), text="Copy new password to clipboard", font=("sans", 13), text_color=palette_color("text"))
        self.copy_password_checkbox.select()
        self.copy_password_checkbox.place(x=30, y=285)

        btn_w = 182
        self.change_preferences_button = ctk.CTkButton(self, width=btn_w, height=42, corner_radius=10, fg_color=palette_color("btn_secondary"), hover_color=palette_color("input_border"), text="Preferences...", text_color=palette_color("surface"), font=("sans", 14), command=self.call_password_preferences_window)
        self.change_preferences_button.place(x=30, y=330)

        self.change_password_button = ctk.CTkButton(self, width=btn_w, height=42, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Change Password", text_color=palette_color("surface"), font=("sans", 14), command=self.change_site_password)
        self.change_password_button.place(x=228, y=330)

        self.error_text = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 13), text_color=palette_color("error"))
        self.error_text.place(relx=0.5, y=390, anchor="center")

        self.grab_set()


    def call_password_preferences_window(self):
        """Opens the password preferences window for this site."""
        self.app.get_preferences_and_initiate_window(self.site_url)


    def change_site_password(self):
        """Requests a new password for this site via the app."""
        self.app.call_change_site_password(self.site_url)

    def display_error(self, msg):
        """Displays an error message in the window."""
        self.error_text.configure(text=msg)

    def close_window(self):
        """Destroys the window and returns whether the user wants the password copied."""
        copy_password = self.copy_password_checkbox.get()
        self.destroy()
        return copy_password