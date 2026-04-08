import customtkinter as ctk

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400

class AuthSelectWindow(ctk.CTkToplevel):

    def __init__(self, app, auth_options, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Choose second authentication factor", font= ("sans", 40), text_color= "black")
        self.title.place(x= 355, y= 25, anchor= "center")

        self.email_auth_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Authenticate with Email", text_color= "black", border_color= "green", command= self.call_email_login)
        self.email_auth_button.place(x = 150, y = 200, anchor = "center")

        if auth_options["voice_auth"]:
            self.voice_auth_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Authenticate with voice", text_color= "black", border_color= "green", state= "normal", command= self.call_voice_auth)
        else:
            self.voice_auth_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Authenticate with voice", text_color= "black", border_color= "green", state= "disabled", command= self.call_voice_auth)
        self.voice_auth_button.place(x = 350, y = 200, anchor=  "center")

        if auth_options["face_auth"]:
            self.face_auth_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Authenticate with face recognition", text_color= "black", border_color= "green", state= "normal", command= self.call_face_recognition)
        else:
            self.face_auth_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Authenticate with face recognition", text_color= "black", border_color= "green", state= "disabled", command= self.call_face_recognition)
        self.face_auth_button.place(x = 550, y = 200, anchor=  "center")

        self.grab_set()

    def call_email_login(self):
        email = self.app.get_email()
        self.close_window()
        self.app.request_login_code(email)

    def call_voice_auth(self):
        self.close_window()
        self.app.run_voice_recording_window()

    def call_face_recognition(self):
        self.close_window()
        self.app.run_video_capture_window()

    def close_window(self):
        self.grab_release()
        self.withdraw()
        self.destroy()
