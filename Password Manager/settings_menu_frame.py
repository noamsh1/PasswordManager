import customtkinter as ctk
from color_palettes import palette_color


class SettingsMenuFrame(ctk.CTkFrame):

    def __init__(self, app, *args, **kwargs):
        super().__init__(master= app.window, fg_color=palette_color("surface2"), *args, **kwargs)

        self.pack_propagate(False)

        self.app = app
        self.is_open = False

        self.close_button = ctk.CTkButton(self, text="✕", width=30, text_color=palette_color("text_dim"), fg_color="transparent", hover_color=palette_color("surface2"), font=("sans", 14), command=self.toggle)
        self.close_button.place(x=5, y=5)

        self.title = ctk.CTkLabel(self, text="Settings", font=("sans", 22, "bold"), text_color=palette_color("text"))
        self.title.pack(pady=20)

        self.title_divider = ctk.CTkFrame(self, height=2, fg_color=palette_color("input_border"))
        self.title_divider.pack(fill="x", padx=16, pady=(0, 10))

        self.theme_switch = ctk.CTkSwitch(self, text="Dark Mode", font=("sans", 13), text_color=palette_color("text"), fg_color=palette_color("input_border"), progress_color=palette_color("accent"), button_color=palette_color("text_dim"), button_hover_color=palette_color("text"), command=self.change_theme)
        self.theme_switch.pack(pady=10, padx=20, anchor="w")


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

    def show_auth_options(self, auth_options):
        self.auth_divider = ctk.CTkFrame(self, height=2, fg_color=palette_color("input_border"))
        self.auth_divider.pack(fill="x", padx=16, pady=(10, 10))

        if not auth_options["voice_auth"]:
            self.add_voice_auth_button = ctk.CTkButton(self, height=36, corner_radius=10, fg_color=palette_color("btn_auth"), hover_color=palette_color("btn_auth_hover"), text="Add Voice Auth", text_color=palette_color("surface"), font=("sans", 13), command=self.setup_voice_auth)
            self.add_voice_auth_button.pack(pady=8, padx=20, fill="x")
        
        if not auth_options["face_auth"]:
            self.add_face_recognition_button = ctk.CTkButton(self, height=36, corner_radius=10, fg_color=palette_color("btn_auth"), hover_color=palette_color("btn_auth_hover"), text="Add Face Recognition", text_color=palette_color("surface"), font=("sans", 13), command=self.setup_face_recognition)
            self.add_face_recognition_button.pack(pady=8, padx=20, fill="x")

    def setup_voice_auth(self):
        self.app.run_voice_recording_window()

    def voice_auth_added(self):
        self.add_voice_auth_button.configure(state= "disabled")

    def setup_face_recognition(self):
        self.app.run_video_capture_window()

    def face_recognition_added(self):
        self.add_face_recognition_button.configure(state= "disabled")