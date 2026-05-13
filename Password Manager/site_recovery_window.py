import customtkinter as ctk
from CTkListbox import *
from color_palettes import palette_color

WINDOW_WIDTH = 440
WINDOW_HEIGHT = 480

class SiteRecoveryWindow(ctk.CTkToplevel):

    def __init__(self, app, deleted_sites, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app    # Reference to the UI instance

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")
        self.configure(fg_color=palette_color("surface"))

        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=45, anchor="center")
        self.icon = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="🔄", fg_color="transparent", text_color=palette_color("surface"), font=("sans", 20))
        self.icon.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self, anchor="center", text="Recover Deleted Sites", font=("sans", 26, "bold"), text_color=palette_color("text"))
        self.title_label.place(relx=0.5, y=95, anchor="center")

        self.subtitle = ctk.CTkLabel(self, anchor="center", text="Select a site to restore", font=("sans", 13), text_color=palette_color("text_dim"))
        self.subtitle.place(relx=0.5, y=120, anchor="center")

        self.deleted_sites_list = CTkListbox(self, height=220, width=360, fg_color=palette_color("surface2"), border_width=2, border_color=palette_color("accent"), highlight_color=palette_color("selected_row"), hover_color=palette_color("surface2"), text_color=palette_color("text"), button_color=palette_color("surface2"), font=("sans", 14), command=self.on_site_selected)
        if deleted_sites is not None:
            for site_url in deleted_sites:
                btn = self.deleted_sites_list.insert("end", site_url)
                btn.configure(corner_radius=10, border_width=2, border_color=palette_color("input_border"), height=42)
        self.deleted_sites_list.place(x=30, y=145)

        self.recover_button = ctk.CTkButton(self, width=200, height=42, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Recover Site", text_color=palette_color("surface"), font=("sans", 14), state="disabled", command=self.recover_site)
        self.recover_button.place(relx=0.5, y=410, anchor="center")

        self.error_text = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 13), text_color=palette_color("error"))
        self.error_text.place(relx=0.5, y=450, anchor="center")

        self.lift()
        self.focus_force()
        self.grab_set()


    def on_site_selected(self, selected_value):
        for btn in self.deleted_sites_list.buttons.values():
            btn.configure(border_color=palette_color("input_border"))
        if self.deleted_sites_list.selected:
            self.deleted_sites_list.selected.configure(border_color=palette_color("accent"))
        self.recover_button.configure(state="normal")

    def recover_site(self):
        """Sends a recovery request for the selected site."""
        site_url = self.deleted_sites_list.get()
        self.app.call_recover_site(site_url)

    def display_error(self, msg):
        """Displays an error message in the window."""
        self.error_text.configure(text=msg)

    def close_window(self):
        """Releases the grab and destroys the window."""
        self.grab_release()
        self.destroy()