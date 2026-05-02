import customtkinter as ctk
from color_palettes import palette_color

WINDOW_WIDTH = 520
WINDOW_HEIGHT = 620

class VideoCaptureWindow(ctk.CTkToplevel):

    def __init__(self, app, cameras_list, is_setup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)
        self.configure(fg_color=palette_color("surface"))

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # ── Icon circle ──
        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=38, anchor="center")
        self.icon_label = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="📷", fg_color="transparent", text_color=palette_color("surface"), font=("Segoe UI Emoji", 20))
        self.icon_label.place(relx=0.5, rely=0.45, anchor="center")

        title_text = "Setup Face Recognition" if is_setup else "Face Recognition"
        self.title_label = ctk.CTkLabel(self, anchor="center", text=title_text, font=("sans", 22, "bold"), text_color=palette_color("text"))
        self.title_label.place(relx=0.5, y=85, anchor="center")

        # ── Camera dropdown ──
        self.cameras_list = cameras_list
        self.camera_dropdown = ctk.CTkComboBox(self, width=240, height=34, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), button_color=palette_color("accent"), button_hover_color=palette_color("accent_hover"), dropdown_fg_color=palette_color("surface"), dropdown_hover_color=palette_color("selected_row"), text_color=palette_color("text"), dropdown_text_color=palette_color("text"), font=("sans", 13), dropdown_font=("sans", 13), values=self.cameras_list, command=self.select_camera)
        self.camera_dropdown.set("Select a camera...")
        self.camera_dropdown.place(relx=0.5, y=118, anchor="center")

        # ── Video feed ──
        self.video_label = ctk.CTkLabel(self, text="", fg_color="transparent", width=460, height=380)
        self.video_label.place(relx=0.5, y=145, anchor="n")

        self.is_loop_running = False

        if is_setup:
            self.setup_face_recognition_button = ctk.CTkButton(self, width=460, height=38, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Setup Face Recognition", text_color=palette_color("surface"), font=("sans", 14), state="disabled", command=self.setup_face_recognition)
            self.setup_face_recognition_button.place(relx=0.5, y=565, anchor="center")
        else:
            self.error_text = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 14), text_color=palette_color("error"))
            self.error_text.place(relx=0.5, y=565, anchor="center")

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
        self.video_label.configure(text="Camera not found", image=None, text_color=palette_color("error"))

    def display_face_recognition_error(self, msg):
        if hasattr(self, "error_text"):
            self.error_text.configure(text= msg)

    def close_window(self):
        self.is_loop_running = False
        if self.app.cap:
            self.app.cap.release()
        self.destroy()