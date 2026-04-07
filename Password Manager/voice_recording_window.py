import customtkinter as ctk

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400

class VoiceRecordingWindow(ctk.CTkToplevel):

    def __init__(self, app, is_setup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Voice Authentication", font= ("sans", 50), text_color= "black")
        self.title.place(x= 355, y= 25, anchor= "center")

        self.start_recording_button = ctk.CTkButton(self, width= 200, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Start Recording", text_color= "black", border_color= "green", command= self.call_voice_recording)
        self.start_recording_button.place(x = 200, y = 150)

        self.text_label = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 20), text_color = "black")
        self.text_label.place(x = 500, y = 200)

        if is_setup:
            self.auth_button = ctk.CTkButton(self, width= 200, height = 50, corner_radius= 5, state= "disabled",fg_color= "green", hover_color= "light green", text= "Setup Voice Authentication", text_color= "black", border_color= "green", command= self.setup_voice_auth)
        else:
            self.auth_button = ctk.CTkButton(self, width= 200, height = 50, corner_radius= 5, state= "disabled",fg_color= "green", hover_color= "light green", text= "Authenticate Voice", text_color= "black", border_color= "green", command= self.call_voice_auth)
        self.auth_button.place(x = 200, y = 250)

        self.error_label = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 20), text_color = "red")
        self.error_label.place(x = 300, y = 350)

        self.grab_set() 

    def call_voice_recording(self):
        self.app.call_start_recording()
        self.auth_button.configure(state= "disabled")
        self.text_label.configure(text= "Recording...")
        self.error_label.configure(text= "")

    def recording_stopped(self):
        self.text_label.configure(text= "Done Recording")
        self.auth_button.configure(state=  "normal")

    def setup_voice_auth(self):
        self.app.call_setup_voice_auth()

    def call_voice_auth(self):
        self.app.call_voice_auth()

    def display_error(self, error_msg):
        self.error_label.configure(text= error_msg)
        self.auth_button.configure(state= "disabled")

    def close_window(self):
        self.destroy()