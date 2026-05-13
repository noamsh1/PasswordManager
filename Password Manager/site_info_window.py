import customtkinter as ctk
import tkinter as tk
from color_palettes import palette_color
from tooltip_window import ToolTip

WINDOW_WIDTH = 440
WINDOW_HEIGHT = 340

class SiteInfoWindow(ctk.CTkToplevel):

    def __init__(self, app, site_username, site_password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app    # Reference to the UI instance
        self.site_username = site_username    # Username for the site
        self.site_password = site_password    # Password for the site

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")
        self.configure(fg_color=palette_color("surface"))

        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=45, anchor="center")
        self.icon = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="🌐", fg_color="transparent", text_color=palette_color("surface"), font=("Segoe UI Emoji", 20))
        self.icon.place(relx=0.5, rely=0.5, anchor="center")

        self.title = ctk.CTkLabel(self, anchor="center", text="Site Info", font=("sans", 26, "bold"), text_color=palette_color("text"))
        self.title.place(relx=0.5, y=92, anchor="center")

        self.username_label = ctk.CTkLabel(self, anchor="w", text="USERNAME", font=("sans", 11, "bold"), text_color=palette_color("text_dim"))
        self.username_label.place(x=30, y=125)
        self.username_field = ctk.CTkEntry(self, width=380, height=38, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), font=("sans", 15), textvariable=tk.StringVar(self, self.site_username), state="disabled")
        self.username_field.place(x=30, y=145)

        self.password_label = ctk.CTkLabel(self, anchor="w", text="PASSWORD", font=("sans", 11, "bold"), text_color=palette_color("text_dim"))
        self.password_label.place(x=30, y=195)
        self.site_password_entry = ctk.CTkEntry(self, width=290, height=38, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), font=("sans", 15), textvariable=tk.StringVar(self, self.site_password), show="•", state="disabled")
        self.site_password_entry.place(x=30, y=215)

        self.site_password_show_button = ctk.CTkButton(self, width=42, height=38, corner_radius=8, fg_color=palette_color("surface2"), hover_color=palette_color("input_border"), text="\uE7B3", font=("Segoe MDL2 Assets", 16), text_color=palette_color("text"), command=self.show_password)
        self.site_password_show_button.place(x=330, y=215)

        self.copy_password_button = ctk.CTkButton(self, width=42, height=38, corner_radius=8, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="📋", font=("Segoe UI Emoji", 14), text_color=palette_color("surface"), command=self.call_copy_password)
        self.copy_password_button.place(x=378, y=215)
        ToolTip(self.copy_password_button, "Copy Password")


        self.password_copied_text = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 13), text_color=palette_color("success"))
        self.password_copied_text.place(relx=0.5, y=275, anchor="center")

        self.grab_set()

    def close_window(self):
        """Destroys the window."""
        self.destroy()


    def call_copy_password(self):
        """Copies the site password to the clipboard and shows a confirmation."""
        self.app.copy_to_clipboard(self.site_password)
        self.password_copied_text.configure(text="Password copied to clipboard")

    def show_password(self):
        self.site_password_entry.configure(show="")
        self.site_password_show_button.configure(text="\uED1A", command=self.hide_password)

    def hide_password(self):
        self.site_password_entry.configure(show="•")
        self.site_password_show_button.configure(text="\uE7B3", command=self.show_password)