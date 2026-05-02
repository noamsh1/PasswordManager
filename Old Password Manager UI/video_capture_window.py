import customtkinter as ctk

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 710

class VideoCaptureWindow(ctk.CTkToplevel):

    def __init__(self, app, cameras_list, is_setup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        if is_setup:
            self.title = ctk.CTkLabel(self, anchor= "center", text= "Setup Face Recognition", font= ("sans", 50), text_color= "black")
        else:
            self.title = ctk.CTkLabel(self, anchor= "center", text= "Face Recognition", font= ("sans", 50), text_color= "black")
        self.title.place(x= 355, y= 25, anchor= "center")

        self.cameras_list = cameras_list
        self.camera_dropdown = ctk.CTkComboBox(self, width= 200, height= 30, values= self.cameras_list, dropdown_font= ("sans", 16), command= self.select_camera)
        self.camera_dropdown.set("Select a camera...")
        self.camera_dropdown.place(x= 355, y= 75, anchor= "center")

        self.video_label = ctk.CTkLabel(self, text= "")
        self.video_label.place(x= 355, y= 100, anchor= "n")

        self.is_loop_running = False

        if is_setup:
            self.setup_face_recognition_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Setup face recognition", text_color= "black", border_color= "green", state= "disabled", command= self.setup_face_recognition)
            self.setup_face_recognition_button.place(x= 355, y= 650, anchor= "center")
        else:
            self.error_text = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 20), text_color= "red")
            self.error_text.place(x= 355, y= 650, anchor= "center")

        self.grab_set() 


    def select_camera(self, choice):
        index = self.cameras_list.index(choice)
        self.app.start_video_recording(index)

    def record_loop(self):
        if self.app.cap is None or not self.app.cap.isOpened():
            self.is_loop_running = False
            return
        
        self.is_loop_running = True
        self.app.get_frames()
        self.after(10, self.record_loop)

    def update_frame(self, img):
        self.video_label.configure(text= "", image= img)

    def face_recognition_loop(self):
        if self.is_loop_running:
            self.app.call_face_recognition()
            self.after(500, self.face_recognition_loop)
        else:
            return
        
    def enable_setup_button(self):
        if hasattr(self, "setup_face_recognition_button"):
            self.setup_face_recognition_button.configure(state= "normal")

    def disable_setup_button(self):
        if hasattr(self, "setup_face_recognition_button"):
            self.setup_face_recognition_button.configure(state= "disabled")

    def setup_face_recognition(self):
        self.app.call_setup_face_recognition()
        

    def display_camera_error(self):
        self.video_label.configure(text= "Camera not found", image= None)

    def display_face_recognition_error(self, msg):
        if hasattr(self, "error_text"):
            self.error_text.configure(text= msg)

    def close_window(self):
        self.is_loop_running = False
        if self.app.cap:
            self.app.cap.release()
        self.destroy()