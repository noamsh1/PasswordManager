import customtkinter as ctk


class SettingsMenuFrame(ctk.CTkFrame):

    def __init__(self, app, auth_options, *args, **kwargs):
        super().__init__(master= app.window, *args, **kwargs)

        self.pack_propagate(False)

        self.app = app
        self.is_open = False

        self.close_button = ctk.CTkButton(self, text= "✕", width= 30, text_color= "black", fg_color= "transparent", hover_color= "gray30", command= self.toggle)
        self.close_button.place(x=5, y=5)

        self.title = ctk.CTkLabel(self, text= "Settings", font= ("sans", 24))
        self.title.pack(pady= 20)

        self.theme_switch = ctk.CTkSwitch(self, text="Dark Mode", command=self.change_theme)
        self.theme_switch.pack(pady=10, padx=20)
        
        if not auth_options["voice_auth"]:
            self.add_voice_auth_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Add voice authentication", text_color= "black", border_color= "green", command= self.setup_voice_auth)
            self.add_voice_auth_button.pack(pady= 10, padx= 30)
        
        if not auth_options["face_auth"]:
            self.add_face_recognition_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Add face recognition", text_color= "black", border_color= "green", command= self.setup_face_recognition)
            self.add_face_recognition_button.pack(pady= 10, padx= 30)



    def toggle(self):
        if not self.is_open:
            self.animate_in()
        else:
            self.animate_out()
        self.is_open = not self.is_open

    def animate_in(self):
        current_relx = float(self.place_info().get('relx', 1.0))
        if current_relx > 0.8:
            self.place(relx=current_relx - 0.02)
            self.after(10, self.animate_in)
        else:
            self.lift()

    def animate_out(self):
        current_relx = float(self.place_info().get('relx', 0.8))
        if current_relx < 1.0:
            self.place(relx=current_relx + 0.02)
            self.after(10, self.animate_out)

    def change_theme(self):
        mode = "dark" if self.theme_switch.get() else "light"
        ctk.set_appearance_mode(mode)

    def setup_voice_auth(self):
        self.app.run_voice_recording_window()

    def voice_auth_added(self):
        self.add_voice_auth_button.configure(state= "disabled")

    def setup_face_recognition(self):
        self.app.run_video_capture_window()

    def face_recognition_added(self):
        self.add_face_recognition_button.configure(state= "disabled")