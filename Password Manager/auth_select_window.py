import customtkinter as ctk
from color_palettes import palette_color

WINDOW_WIDTH = 440
WINDOW_HEIGHT = 420

class AuthSelectWindow(ctk.CTkToplevel):

    def __init__(self, app, auth_options, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app    # Reference to the UI instance

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")
        self.configure(fg_color=palette_color("surface"))

        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=45, anchor="center")
        self.icon = ctk.CTkLabel(self.icon_circle, width=0, height=0, anchor="center", text="🔐", fg_color="transparent", text_color=palette_color("surface"), font=("Segoe UI Emoji", 24))
        self.icon.place(relx=0.5, rely=0.5, anchor="center")

        self.title = ctk.CTkLabel(self, anchor="center", text="Choose 2FA Method", font=("sans", 28, "bold"), text_color=palette_color("text"))
        self.title.place(relx=0.5, y=95, anchor="center")
        self.subtitle = ctk.CTkLabel(self, anchor="center", text="Select a second authentication factor", font=("sans", 14), text_color=palette_color("text_dim"))
        self.subtitle.place(relx=0.5, y=125, anchor="center")

        row_w = 380
        row_h = 64

        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.place(relx=0.5, y=155, anchor="n")

        self._email_row = self._make_option_row(self.options_frame, row_w, row_h, "📧", "Email Code", "Receive a verification code via email", True, self.call_email_login)
        self._email_row.pack(pady=(0, 5))
        self._voice_row = self._make_option_row(self.options_frame, row_w, row_h, "🎤", "Voice Auth", "Authenticate with your voice", auth_options["voice_auth"], self.call_voice_auth)
        self._voice_row.pack(pady=5)
        self._face_row = self._make_option_row(self.options_frame, row_w, row_h, "📷", "Face Recognition", "Authenticate with your face", auth_options["face_auth"], self.call_face_recognition)
        self._face_row.pack(pady=(5, 0))

        self.grab_set()

    def _make_option_row(self, parent, w, h, icon, title, desc, enabled, command):
        border = palette_color("btn_auth") if enabled else palette_color("divider")
        bg = palette_color("surface2") if enabled else palette_color("disabled_bg")
        text_col = palette_color("text") if enabled else palette_color("disabled_text")
        dim_col = palette_color("text_dim") if enabled else palette_color("disabled_text")
        hover_bg = palette_color("input_border") if enabled else palette_color("disabled_bg")

        frame = ctk.CTkFrame(parent, width=w, height=h, corner_radius=10, fg_color=bg, border_color=border, border_width=2)

        icon_lbl = ctk.CTkLabel(frame, text=icon, font=("Segoe UI Emoji", 18), text_color=text_col, fg_color="transparent")
        icon_lbl.place(x=24, rely=0.5, anchor="center")
        title_lbl = ctk.CTkLabel(frame, text=title, font=("sans", 14, "bold"), text_color=text_col, fg_color="transparent")
        title_lbl.place(x=46, rely=0.32, anchor="w")
        desc_lbl = ctk.CTkLabel(frame, text=desc, font=("sans", 11), text_color=dim_col, fg_color="transparent")
        desc_lbl.place(x=46, rely=0.68, anchor="w")

        if enabled:
            for widget in [frame, icon_lbl, title_lbl, desc_lbl]:
                widget.bind("<Enter>", lambda e, f=frame: f.configure(fg_color=hover_bg))
                widget.bind("<Leave>", lambda e, f=frame: f.configure(fg_color=bg))
                widget.bind("<Button-1>", lambda e, cmd=command: cmd())
        else:
            nc_lbl = ctk.CTkLabel(frame, text="Not configured", font=("sans", 11), text_color=dim_col, fg_color="transparent")
            nc_lbl.place(x=w - 16, rely=0.5, anchor="e")

        return frame

    def call_email_login(self):
        """Closes the window and initiates email code login."""
        email = self.app.get_email()
        self.close_window()
        self.app.request_login_code(email)

    def call_voice_auth(self):
        """Closes the window and opens the voice recording window."""
        self.close_window()
        self.app.run_voice_recording_window()

    def call_face_recognition(self):
        """Closes the window and opens the video capture window."""
        self.close_window()
        self.app.run_video_capture_window()

    def close_window(self):
        """Releases the grab and destroys the window."""
        self.grab_release()
        self.withdraw()
        self.destroy()
