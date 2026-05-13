import time
import customtkinter as ctk
from color_palettes import palette_color

WINDOW_WIDTH = 440
WINDOW_HEIGHT = 420

MIN_RECORDING_TIME = 5

class VoiceRecordingWindow(ctk.CTkToplevel):

    def __init__(self, app, is_setup, max_recording_time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app    # Reference to the UI instance

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)
        self.configure(fg_color=palette_color("surface"))

        # ── Icon circle ──
        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=38, anchor="center")
        self.icon_label = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="🎤", fg_color="transparent", text_color=palette_color("surface"), font=("Segoe UI Emoji", 22))
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self, anchor="center", text="Voice Authentication", font=("sans", 22, "bold"), text_color=palette_color("text"))
        self.title_label.place(relx=0.5, y=100, anchor="center")

        # ── Progress bar ──
        self.max_recording_time = max_recording_time
        self.progress_bar_value = ctk.DoubleVar(value=0.0)
        slider_width = 380
        slider_frame = ctk.CTkFrame(self, width=slider_width, height=50, fg_color="transparent")
        slider_frame.place(relx=0.5, y=165, anchor="center")

        self.progress_bar = ctk.CTkSlider(slider_frame, width=slider_width, height=20, from_=0, to=self.max_recording_time, variable=self.progress_bar_value, state="disabled", button_length=0, fg_color=palette_color("input_border"), progress_color=palette_color("accent"), button_color=palette_color("accent"), button_hover_color=palette_color("accent"))
        self.progress_bar.place(relx=0.5, y=0, anchor="n")

        # ── Min recording time marker ──
        marker_relx = MIN_RECORDING_TIME / self.max_recording_time
        self.min_marker = ctk.CTkFrame(slider_frame, width=2, height=10, fg_color=palette_color("text_dim"), corner_radius=0)
        self.min_marker.place(relx=marker_relx, y=20, anchor="n")
        self.min_label = ctk.CTkLabel(slider_frame, width=0, height=0, text="Minimum", font=("sans", 10), text_color=palette_color("text_dim"))
        self.min_label.place(relx=marker_relx, rely=1.0, anchor="s")

        self.text_label = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 13), text_color=palette_color("text_dim"))
        self.text_label.place(relx=0.5, y=215, anchor="center")

        # ── Recording buttons ──
        btn_w = 182
        self.start_recording_button = ctk.CTkButton(self, width=btn_w, height=38, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Start Recording", text_color=palette_color("surface"), font=("sans", 14), command=self.call_voice_recording)
        self.start_recording_button.place(x=30, y=245)

        self.stop_recording_button = ctk.CTkButton(self, width=btn_w, height=38, corner_radius=10, fg_color=palette_color("surface2"), hover_color=palette_color("input_border"), text="Stop Recording", text_color=palette_color("text"), font=("sans", 14), state="disabled", command=self.call_stop_recording)
        self.stop_recording_button.place(x=WINDOW_WIDTH - 30 - btn_w, y=245)

        # ── Auth button ──
        if is_setup:
            self.auth_button = ctk.CTkButton(self, width=380, height=38, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Setup Voice Authentication", text_color=palette_color("surface"), font=("sans", 14), state="disabled", command=self.setup_voice_auth)
        else:
            self.auth_button = ctk.CTkButton(self, width=380, height=38, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Authenticate Voice", text_color=palette_color("surface"), font=("sans", 14), state="disabled", command=self.call_voice_auth)
        self.auth_button.place(relx=0.5, y=315, anchor="center")

        self.error_label = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 14), text_color=palette_color("error"))
        self.error_label.place(relx=0.5, y=365, anchor="center")

        self.is_recording = False    # Whether voice recording is currently active
        self.grab_set()

    def call_voice_recording(self):
        """Starts voice recording and begins the progress bar loop."""
        self.app.call_start_recording()
        self.is_recording = True
        self._start_time = time.time()
        self.progress_bar_value = 0
        self.progress_bar.set(self.progress_bar_value)
        self.after(10, self.recording_progress_loop)
        self.auth_button.configure(state= "disabled")
        self.start_recording_button.configure(state= "disabled")
        self.stop_recording_button.configure(state= "disabled")
        self.text_label.configure(text= "Recording...")
        self.error_label.configure(text= "")

    def recording_progress_loop(self):
        """Updates the progress bar while recording until max time is reached."""
        if self.is_recording and self.progress_bar_value < self.max_recording_time:
            self.progress_bar_value = min(time.time() - self._start_time, self.max_recording_time)
            self.progress_bar.set(self.progress_bar_value)
            if self.progress_bar_value >= MIN_RECORDING_TIME:
                self.stop_recording_button.configure(state= "enabled")
            self.after(10, self.recording_progress_loop)

    def call_stop_recording(self):
        """Stops voice recording via the app."""
        self.app.call_stop_recording()

    def recording_stopped(self):
        """Updates the UI to show that recording has stopped."""
        self.is_recording = False
        self.text_label.configure(text= "Done Recording")
        self.auth_button.configure(state=  "normal")
        self.start_recording_button.configure(state= "enabled")
        self.stop_recording_button.configure(state= "disabled")

    def setup_voice_auth(self):
        """Sends the recorded voice to the server for setup."""
        self.app.call_setup_voice_auth()

    def call_voice_auth(self):
        """Sends the recorded voice to the server for authentication."""
        self.app.call_voice_auth()

    def display_error(self, error_msg):
        """Displays an error message and disables the auth button."""
        self.error_label.configure(text= error_msg)
        self.auth_button.configure(state= "disabled")

    def close_window(self):
        """Destroys the window."""
        self.destroy()