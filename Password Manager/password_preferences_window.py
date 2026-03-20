import customtkinter as ctk
from password_handler import DEFAULT_LENGTH, DEFAULT_SPECIAL, DEFAULT_SETTINGS, MINIMUM_PASSWORD_LENGTH

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400

class PasswordPreferencesWindow(ctk.CTkToplevel):

    def __init__(self, app, settings= None, site_url = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")

        if settings is None:
            settings = DEFAULT_SETTINGS

        self.site_url = site_url

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Password Generation Preferences", font= ("sans", 40), text_color= "black")
        self.title.place(x= 355, y= 40, anchor= "center")

        self.maximum_length_text = ctk.CTkLabel(self, anchor= "center", text= "Maximum Length:", font= ("sans", 25), text_color= "black")
        self.maximum_length_text.place(x= 100, y= 100)

        self.maximum_length_entry = ctk.CTkEntry(self, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
        self.maximum_length_entry.insert(0, settings.get("max_length"))
        self.maximum_length_entry.place(x= 300, y= 100)        

        self.should_include_text = ctk.CTkLabel(self, anchor= "center", text= "Password should include:", font= ("sans", 25), text_color= "black")
        self.should_include_text.place(x= 80, y= 150)

        self.include_vars = {}

        for i, (label, value) in enumerate(settings["include"].items()):
                    var = ctk.BooleanVar(value=value)
                    self.include_vars[label] = var
                    cb = ctk.CTkCheckBox(self, width = 50, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= label, font= ("sans", 18), variable= var, command= lambda l = label: self.check_inclusion_selection(l))
                    cb.place(x=110, y=180 + (i * 30))

        self.special_allowed_entry = ctk.CTkEntry(self, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
        self.special_allowed_entry.insert(0, settings.get("special_allowed"))
        if self.include_vars["Special"].get():
            self.special_allowed_entry.place(x= 210, y= 270)

        # self.include_upper_var = ctk.BooleanVar(value= include_upper)
        # self.include_upper_checkbox = ctk.CTkCheckBox(self, width = 50, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= "Upper", font= ("sans", 18), variable= self.include_upper_var)
        # self.include_upper_checkbox.place(x= 110, y= 180)

        # self.include_lower_var = ctk.BooleanVar(value= include_lower)
        # self.include_lower_checkbox = ctk.CTkCheckBox(self, width = 50, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= "Lower", font= ("sans", 18), variable = self.include_lower_var)
        # self.include_lower_checkbox.place(x= 110, y= 210)

        # self.include_num_var = ctk.BooleanVar(value= include_num)
        # self.include_num_checkbox = ctk.CTkCheckBox(self, width = 50, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= "Number", font= ("sans", 18), variable = self.include_num_var)
        # self.include_num_checkbox.place(x= 110, y= 240)

        # self.include_special_var = ctk.BooleanVar(value= include_special)
        # self.include_special_checkbox = ctk.CTkCheckBox(self, width = 50, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= "Special", font= ("sans", 18), variable = self.include_special_var)
        # self.include_special_checkbox.place(x= 110, y= 270)

        self.can_start_with_text = ctk.CTkLabel(self, anchor= "center", text= "Password can start with:", font= ("sans", 25), text_color= "black")
        self.can_start_with_text.place(x= 400, y= 150)

        self.start_vars = {}
        self.start_cb = {}

        for i, (label, value) in enumerate(settings["start"].items()):
            var = ctk.BooleanVar(value=value)
            self.start_vars[label] = var
            cb = ctk.CTkCheckBox(self, width = 50, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= label, font= ("sans", 18), variable= var, command= lambda l = label : self.check_start_selection(l))
            if not self.include_vars[label].get():
                cb.configure(state= "disabled")
            cb.place(x=430, y=180 + (i * 30))
            self.start_cb[label] = cb
            
        self.special_allowed_start_entry = ctk.CTkEntry(self, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
        self.special_allowed_start_entry.insert(0, settings.get("special_allowed_start"))
        if self.start_vars["Special"].get():
            self.special_allowed_start_entry.place(x= 530, y= 270)

        # self.start_with_upper_var = ctk.BooleanVar(value= can_start_with_upper)
        # self.start_with_upper_checkbox = ctk.CTkCheckBox(self, width = 50, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= "Upper", font= ("sans", 18), variable = self.start_with_upper_var)
        # self.start_with_upper_checkbox.place(x= 430, y= 180)

        # self.start_with_lower_var = ctk.BooleanVar(value= can_start_with_lower)
        # self.start_with_lower_checkbox = ctk.CTkCheckBox(self, width = 50, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= "Lower", font= ("sans", 18), variable= self.start_with_lower_var)
        # self.start_with_lower_checkbox.place(x= 430, y= 210)

        # self.start_with_num_var = ctk.BooleanVar(value= can_start_with_num)
        # self.start_with_num_checkbox = ctk.CTkCheckBox(self, width = 50, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= "Number", font= ("sans", 18), variable= self.start_with_num_var)
        # self.start_with_num_checkbox.place(x= 430, y= 240)

        # self.start_with_special_var = ctk.BooleanVar(value= can_start_with_special)
        # self.start_with_special_checkbox = ctk.CTkCheckBox(self,width = 50, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= "Special", font= ("sans", 18), variable= self.start_with_special_var)
        # self.start_with_special_checkbox.place(x= 430, y= 270)

        self.save_preferences_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Save Preferences", text_color= "black", border_color= "green", command= self.save_preferences)
        self.save_preferences_button.place(x = 280, y= 320)

        self.error_label = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 20), text_color= "red")
        self.error_label.place(x= 100, y= 370)


        self.grab_set()

    
    def check_inclusion_selection(self, label):
        count_active = sum(var.get() for var in self.include_vars.values())
        if count_active < 1:
            self.include_vars[label].set(True)
        elif self.include_vars[label].get() == False:
            self.start_vars[label].set(False)
            self.start_cb[label].configure(state= "disabled")
            if label == "Special":
                self.special_allowed_entry.place_forget()
                self.special_allowed_start_entry.place_forget()
        else:
            self.start_cb[label].configure(state= "normal")
            if label == "Special":
                self.special_allowed_entry.place(x= 210, y= 270)

    def check_start_selection(self, label):
        count_active = sum(var.get() for var in self.start_vars.values())
        if count_active < 1:
            self.start_vars[label].set(True)
        elif label == "Special":
            if self.start_vars[label].get():
                self.special_allowed_start_entry.place(x= 530, y= 270)
            else:
                self.special_allowed_start_entry.place_forget()

    def save_preferences(self):
        preferences = {}
        try:
            length = int(self.maximum_length_entry.get())
            if length < MINIMUM_PASSWORD_LENGTH:
                raise ValueError
        except ValueError:
            self.display_error(f"Maximum length should be a number greater than {MINIMUM_PASSWORD_LENGTH}")
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
        filtered_set = set(str)
        filtered_string = ""
        for i in filtered_set:
            filtered_string += i
        return filtered_string

    def display_error(self, msg):
        self.error_label.configure(text= msg)

    def close_window(self):
        self.destroy()


