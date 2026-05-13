import customtkinter as ctk
from color_palettes import palette_color
from password_handler import DEFAULT_SETTINGS, MINIMUM_PASSWORD_LENGTH, MAXIMUM_PASSWORD_LENGTH

WINDOW_WIDTH = 520
WINDOW_HEIGHT = 540

COL_LEFT = 30
COL_RIGHT = 270
CB_Y_START = 262
CB_Y_STEP = 32

class PasswordPreferencesWindow(ctk.CTkToplevel):

    def __init__(self, app, settings=None, site_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app    # Reference to the UI instance

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")
        self.configure(fg_color=palette_color("surface"))

        if settings is None:
            settings = DEFAULT_SETTINGS

        self.site_url = site_url    # URL of the site these preferences apply to, or None during registration

        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=45, anchor="center")
        self.icon = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="🔑", fg_color="transparent", text_color=palette_color("surface"), font=("sans", 20))
        self.icon.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self, anchor="center", text="Password Preferences", font=("sans", 26, "bold"), text_color=palette_color("text"))
        self.title_label.place(relx=0.5, y=95, anchor="center")

        self.section_label = ctk.CTkLabel(self, anchor="w", text="GENERATION RULES", font=("sans", 11, "bold"), text_color=palette_color("accent"))
        self.section_label.place(x=COL_LEFT, y=130)
        self.divider = ctk.CTkFrame(self, width=460, height=2, fg_color=palette_color("divider"))
        self.divider.place(x=COL_LEFT, y=150)

        self.maximum_length_text = ctk.CTkLabel(self, anchor="w", text="Maximum Length", font=("sans", 13), text_color=palette_color("text_dim"))
        self.maximum_length_text.place(x=COL_LEFT, y=160)
        self.maximum_length_entry = ctk.CTkEntry(self, width=120, height=38, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), font=("sans", 14))
        self.maximum_length_entry.insert(0, settings.get("max_length"))
        self.maximum_length_entry.place(x=COL_LEFT, y=183)

        self.includes_header = ctk.CTkLabel(self, anchor="w", text="PASSWORD INCLUDES", font=("sans", 11, "bold"), text_color=palette_color("accent"))
        self.includes_header.place(x=COL_LEFT, y=232)
        self.start_header = ctk.CTkLabel(self, anchor="w", text="CAN START WITH", font=("sans", 11, "bold"), text_color=palette_color("accent"))
        self.start_header.place(x=COL_RIGHT, y=232)

        self.include_vars = {}
        for i, (label, value) in enumerate(settings["include"].items()):
            var = ctk.BooleanVar(value=value)
            self.include_vars[label] = var
            cb = ctk.CTkCheckBox(self, width=20, height=20, corner_radius=4, border_color=palette_color("input_border"), fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), checkmark_color=palette_color("surface"), text=label, font=("sans", 13), text_color=palette_color("text"), variable=var, command=lambda l=label: self.check_inclusion_selection(l))
            cb.place(x=COL_LEFT, y=CB_Y_START + (i * CB_Y_STEP))

        self.special_entry_y = CB_Y_START + (len(settings["include"]) * CB_Y_STEP)
        self.special_allowed_entry = ctk.CTkEntry(self, width=210, height=34, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), font=("sans", 13))
        self.special_allowed_entry.insert(0, settings.get("special_allowed"))
        if self.include_vars["Special"].get():
            self.special_allowed_entry.place(x=COL_LEFT, y=self.special_entry_y)

        self.start_vars = {}
        self.start_cb = {}
        for i, (label, value) in enumerate(settings["start"].items()):
            var = ctk.BooleanVar(value=value)
            self.start_vars[label] = var
            cb = ctk.CTkCheckBox(self, width=20, height=20, corner_radius=4, border_color=palette_color("input_border"), fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), checkmark_color=palette_color("surface"), text=label, font=("sans", 13), text_color=palette_color("text"), variable=var, command=lambda l=label: self.check_start_selection(l))
            if not self.include_vars[label].get():
                cb.configure(state="disabled")
            cb.place(x=COL_RIGHT, y=CB_Y_START + (i * CB_Y_STEP))
            self.start_cb[label] = cb

        self.special_allowed_start_entry = ctk.CTkEntry(self, width=210, height=34, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), font=("sans", 13))
        self.special_allowed_start_entry.insert(0, settings.get("special_allowed_start"))
        if self.start_vars["Special"].get():
            self.special_allowed_start_entry.place(x=COL_RIGHT, y=self.special_entry_y)

        self.save_preferences_button = ctk.CTkButton(self, width=200, height=42, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Save Preferences", text_color=palette_color("surface"), font=("sans", 14), command=self.save_preferences)
        self.save_preferences_button.place(relx=0.5, y=460, anchor="center")

        self.error_label = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 13), text_color=palette_color("error"))
        self.error_label.place(relx=0.5, y=510, anchor="center")

        self.grab_set()


    def check_inclusion_selection(self, label):
        """Enforces at least one include checkbox and syncs the start checkbox state."""
        count_active = sum(var.get() for var in self.include_vars.values())
        if count_active < 1:
            self.include_vars[label].set(True)
        elif self.include_vars[label].get() == False:
            self.start_vars[label].set(False)
            self.start_cb[label].configure(state="disabled")
            if label == "Special":
                self.special_allowed_entry.place_forget()
                self.special_allowed_start_entry.place_forget()
        else:
            self.start_cb[label].configure(state="normal")
            if label == "Special":
                self.special_allowed_entry.place(x=COL_LEFT, y=self.special_entry_y)

    def check_start_selection(self, label):
        """Enforces at least one start checkbox and toggles the special characters entry."""
        count_active = sum(var.get() for var in self.start_vars.values())
        if count_active < 1:
            self.start_vars[label].set(True)
        elif label == "Special":
            if self.start_vars[label].get():
                self.special_allowed_start_entry.place(x=COL_RIGHT, y=self.special_entry_y)
            else:
                self.special_allowed_start_entry.place_forget()

    def save_preferences(self):
        """Validates the preferences and sends them to the app."""
        preferences = {}
        try:
            length = int(self.maximum_length_entry.get())
            if length < MINIMUM_PASSWORD_LENGTH or length > MAXIMUM_PASSWORD_LENGTH:
                raise ValueError
        except ValueError:
            self.display_error(f"Maximum length should be a number equal to or greater than {MINIMUM_PASSWORD_LENGTH}\nAnd lower than {MAXIMUM_PASSWORD_LENGTH}")
            return
        
        preferences["max_length"] = length
        preferences["include"] = dict((label, var.get()) for label, var in self.include_vars.items())
        preferences["special_allowed"] = self._remove_duplicates(self.special_allowed_entry.get())
        preferences["start"] = dict((label, var.get()) for label, var in self.start_vars.items())

        if sum(var for var in preferences["start"].values()) < 1:
            self.display_error("At least one 'start with' checkbox must be selected")
            return
        
        preferences["special_allowed_start"] = self._remove_duplicates(self.special_allowed_start_entry.get())
        self.app.save_password_preferences(preferences, self.site_url)

    def _remove_duplicates(self, str):
        """Receives a string and returns it with duplicate characters removed."""
        filtered_set = set(str)
        filtered_string = ""
        for i in filtered_set:
            filtered_string += i
        return filtered_string

    def display_error(self, msg):
        """Displays an error message in the window."""
        self.error_label.configure(text=msg)

    def close_window(self):
        """Destroys the window."""
        self.destroy()


