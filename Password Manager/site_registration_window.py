import customtkinter as ctk
from color_palettes import palette_color

WINDOW_WIDTH = 440
WINDOW_HEIGHT = 460

class SiteRegistrationWindow(ctk.CTkToplevel):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")
        self.configure(fg_color=palette_color("surface"))

        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=45, anchor="center")
        self.icon = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="+", fg_color="transparent", text_color=palette_color("surface"), font=("sans", 28, "bold"))
        self.icon.place(relx=0.5, rely=0.5, anchor="center")

        self.title = ctk.CTkLabel(self, anchor="center", text="Register New Site", font=("sans", 26, "bold"), text_color=palette_color("text"))
        self.title.place(relx=0.5, y=95, anchor="center")

        self.section_label = ctk.CTkLabel(self, anchor="w", text="SITE DETAILS", font=("sans", 11, "bold"), text_color=palette_color("accent"))
        self.section_label.place(x=30, y=130)
        self.divider = ctk.CTkFrame(self, width=380, height=2, fg_color=palette_color("divider"))
        self.divider.place(x=30, y=150)

        self.site_url_text = ctk.CTkLabel(self, anchor="w", text="Site URL", font=("sans", 13), text_color=palette_color("text_dim"))
        self.site_url_text.place(x=30, y=160)
        self.site_url_entry = ctk.CTkEntry(self, width=380, height=38, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text_color=palette_color("placeholder"), font=("sans", 14), placeholder_text="e.g. github.com")
        self.site_url_entry.place(x=30, y=183)

        self.site_username_text = ctk.CTkLabel(self, anchor="w", text="Username for this site", font=("sans", 13), text_color=palette_color("text_dim"))
        self.site_username_text.place(x=30, y=230)
        self.site_username_entry = ctk.CTkEntry(self, width=380, height=38, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text_color=palette_color("placeholder"), font=("sans", 14), placeholder_text="Enter username")
        self.site_username_entry.place(x=30, y=253)

        self.copy_password_checkbox = ctk.CTkCheckBox(self, width=20, height=20, corner_radius=4, border_color=palette_color("input_border"), fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), checkmark_color=palette_color("surface"), text="Copy password after registration", font=("sans", 13), text_color=palette_color("text"))
        self.copy_password_checkbox.select()
        self.copy_password_checkbox.place(x=30, y=305)

        btn_w = 182
        self.change_preferences_button = ctk.CTkButton(self, width=btn_w, height=42, corner_radius=10, fg_color=palette_color("btn_secondary"), hover_color=palette_color("input_border"), text="Preferences...", text_color=palette_color("surface"), font=("sans", 14), command=self.call_password_preferences_window)
        self.change_preferences_button.place(x=30, y=350)

        self.register_button = ctk.CTkButton(self, width=btn_w, height=42, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Register Site", text_color=palette_color("surface"), font=("sans", 14), command=self.call_register_site)
        self.register_button.place(x=228, y=350)

        self.error_text = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 13), text_color=palette_color("error"))
        self.error_text.place(relx=0.5, y=410, anchor="center")

        self.preferences = None

        self.grab_set()


    def call_password_preferences_window(self):
        self.app.run_password_preferences_window(self.preferences)


    def call_register_site(self):
        site_url = self.site_url_entry.get()
        if site_url == "":
            self.display_registration_error("You must enter a site url before registration")
            return
        site_username = self.site_username_entry.get()
        if site_username == "":
            self.display_registration_error("You must enter a username before registration")
            return
        self.app.call_register_site(site_url, site_username, self.preferences)

    def display_registration_error(self, msg):
        self.error_text.configure(text=msg)

    def close_window(self):
        copy_password = self.copy_password_checkbox.get()
        self.destroy()
        return copy_password