import customtkinter as ctk
import threading
from PIL import Image
from video_manager import VideoManager
from signup_window import SignupWindow
from login_window import LoginWindow
from auth_select_window import AuthSelectWindow
from code_login_window import CodeLoginWindow
from voice_recording_window import VoiceRecordingWindow
from video_capture_window import VideoCaptureWindow
from security_questions_setup_window import SecurityQuestionsSetupWindow
from security_questions_auth_window import SecurityQuestionsAuthWindow
from reset_password_window import ResetPasswordWindow
from site_registration_window import SiteRegistrationWindow
from password_preferences_window import PasswordPreferencesWindow
from site_info_window import SiteInfoWindow
from change_password_window import ChangePasswordWindow
from site_recovery_window import SiteRecoveryWindow
from settings_menu_frame import SettingsMenuFrame
from CTkListbox import *
from client_status import Status

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 675

class UI:

    def __init__(self, client):
        self.window = ctk.CTk()
        self.window.wm_title("Password Manager")
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.resizable(False, False)
        self.client = client

        self.title = ctk.CTkLabel(self.window, anchor= "center", text= "Password Manager", font= ("sans", 50), text_color= "black")
        self.title.place(x= 100, y= 50, anchor= "nw")

        self.login_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Login", text_color= "black", border_color= "green", command= self.run_login_window)
        self.login_button.place(x = 900, y= 50)

        self.login_window = None

        self.reset_password_window = None

        self.signup_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Signup", text_color= "black", border_color= "green", command= self.run_signup_window)
        self.signup_button.place(x= 700, y= 50)

        self.signup_window = None

        self.auth_select_window = None
        self.code_login_window = None
        self.voice_recording_window = None

        self.cap = None
        self.current_camera_index = -1
        self.rgb_small_frame = None
        self.video_capture_window = None

        self.security_questions_window = None

        self.register_site_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Register Site", text_color= "black", border_color= "green", command= self.run_site_registration_window)
        self.username_text = ctk.CTkLabel(self.window, anchor= "center", text= "", font= ("sans", 25), text_color= "black")
        self.site_registration_window = None

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.load_registered_sites)
        self.search_box = ctk.CTkEntry(self.window, width = 950, height= 30, corner_radius= 3, placeholder_text= "Search site", textvariable= self.search_var)
        self.delete_search_button = ctk.CTkButton(self.window, width= 50, height= 30, corner_radius= 3, text= "Delete search", command= lambda: self.search_var.set(""))

        self.curret_site_selection = None
        self.registered_sites_list = CTkListbox(self.window, height= 350, width= 1000, command= self.enable_site_buttons)

        self.site_info_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "View site info", text_color= "black", border_color= "green", state= "disabled", command= self.show_selected_site_info)
        self.site_info_window = None

        self.change_password_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Change site password", text_color= "black", border_color= "green", state= "disabled", command= self.initiate_change_password_window)
        self.change_password_window = None

        self.delete_site_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "dark red", hover_color= "red", text= "Delete site", text_color= "black", border_color= "dark red", state= "disabled", command= self.delete_site)

        self.password_preferences_window = None

        self.recover_site_button = ctk.CTkButton(self.window, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Recover site", text_color= "black", border_color= "green", command= self.run_site_recovery_window)
        self.site_recovery_window = None


    def run(self):
        self.window.mainloop()

    def run_signup_window(self):
        self.client.change_status(Status.SIGNING_IN)
        if self.signup_window is None or not self.signup_window.winfo_exists():
            self.signup_window = SignupWindow(self)
        else:
            self.signup_window.focus()

    def call_signup(self, username, password, email, phone_number):
        self.client.signup(username, password, email, phone_number)

    def display_signup_error(self, msg):
        self.signup_window.display_signup_error(msg)

    def signup_successful(self, username, password):
        self.signup_window.close_window()
        self.call_login(username, password)

    def run_login_window(self):
        self.client.change_status(Status.LOGGING_IN)
        if self.login_window is None or not self.login_window.winfo_exists():
            self.login_window = LoginWindow(self)
        else:
            self.login_window.focus()
        

    def call_login(self, username, password):
        self.client.login(username, password)

    def display_login_error(self, msg):
        self.login_window.display_login_error(msg)

    def login_succesful(self, username, password):
        if not self.login_window is None:
            self.login_window.close_window()
        if self.client.status == Status.SIGNING_IN:
            self.setup_user(username)
        elif self.client.status == Status.LOGGING_IN:
            self.run_auth_select_window()


    def get_email(self):
        return self.client.get_email()


    def call_get_auth_options(self):
        return self.client.get_auth_options()

    def run_auth_select_window(self):
        if self.auth_select_window is None or not self.auth_select_window.winfo_exists():
            auth_options = self.call_get_auth_options()
            self.auth_select_window = AuthSelectWindow(self, auth_options)
        else:
            self.auth_select_window.focus()

    def run_security_questions_setup_window(self, ):
        if self.security_questions_window is None or not self.security_questions_window.winfo_exists():
            security_questions_list = self.call_get_security_questions_list()
            self.security_questions_window = SecurityQuestionsSetupWindow(self, security_questions_list, self.client.chosen_questions_dict)
        else:
            self.security_questions_window.focus()

    def call_get_security_questions_list(self):
        return self.client.get_security_questions_list()
    
    def call_setup_security_questions(self, chosen_questions_dict):
        self.client.setup_security_questions(chosen_questions_dict)

    def questions_setup_successful(self):
        self.security_questions_window.close_window()
        self.signup_window.questions_setup_successful()

    def run_security_questions_auth_window(self, user_security_questions):
        self.login_window.close_window()
        if self.security_questions_window is None or not self.security_questions_window.winfo_exists():
            self.security_questions_window = SecurityQuestionsAuthWindow(self, user_security_questions)
        else:
            self.security_questions_window.focus()

    def call_get_user_security_questions(self, username):
        self.client.get_user_security_questions(username)

    def call_check_security_answers(self, answers):
        self.client.check_security_answers(answers)

    def security_answers_correct(self):
        self.client.change_status(Status.RECOVERING_PASSWORD)
        self.security_questions_window.close_window()
        self.run_auth_select_window()

    def security_answers_incorrect(self):
        self.security_questions_window.display_error("One or more answers are incorrect")

    def run_reset_password_window(self):
        if self.reset_password_window is None or not self.reset_password_window.winfo_exists():
            self.reset_password_window = ResetPasswordWindow(self)
        else:
            self.reset_password_window.focus()

    def call_reset_password(self, new_password):
        self.client.reset_password(new_password)

    def password_reset_successful(self, username):
        self.reset_password_window.close_window()
        self.setup_user(username)

    def run_code_login_window(self, client_email):
        if self.code_login_window is None or not self.code_login_window.winfo_exists():
            self.code_login_window = CodeLoginWindow(self, client_email)
            self.code_login_window.focus()
            self.code_login_window.lift()
        else:
            self.code_login_window.focus()
            self.code_login_window.lift()

    def request_login_code(self, client_email):
        was_code_sent = self.client.request_code(client_email)
        if was_code_sent:
            self.run_code_login_window(client_email)
    
    def call_is_email_valid(self, email):
        result = self.client.is_email_valid(email)
        if result:
            self.signup_window.email_valid()
        else:
            self.signup_window.email_invalid()

    def call_check_code(self, code):
        self.client.code_login(code)

    def signup_code_correct(self):
        self.code_login_window.close_window()
        if self.client.can_user_signup():
            self.signup_window.can_signup()
            self.signup_window.email_verified()


    def login_code_correct(self):
        self.code_login_window.close_window()
        self.auth_successful()

    def code_incorrect(self):
        self.code_login_window.incorrect_code_feedback()

    def code_expired(self):
        self.code_login_window.display_code_expired_msg()

    def run_voice_recording_window(self):
        if self.voice_recording_window is None or not self.voice_recording_window.winfo_exists():
            if self.client.status == Status.SIGNING_IN or self.client.status == Status.NORMAL:
                is_setup = True
            else:
                is_setup = False
            self.voice_recording_window = VoiceRecordingWindow(self, is_setup)
            self.voice_recording_window.focus()
            self.voice_recording_window.lift()
        else:
            self.voice_recording_window.focus()
            self.voice_recording_window.lift()

    def call_start_recording(self):
        self.client.start_voice_recording()

    def recording_stopped(self):
        self.voice_recording_window.recording_stopped()

    def call_setup_voice_auth(self):
        self.client.setup_voice_auth()

    def voice_auth_setup_successful(self):
        self.voice_recording_window.close_window()
        if self.client.status == Status.SIGNING_IN:
            self.signup_window.voice_auth_added()
        elif self.client.status == Status.NORMAL:
            self.settings_menu.voice_auth_added()

    def signature_extraction_error(self):
        self.voice_recording_window.display_error("Could not extract voice signature. Please record again.")

    def call_voice_auth(self):
        self.client.voice_auth()

    def voice_auth_successful(self):
        self.voice_recording_window.close_window()
        self.auth_successful()

    def voice_auth_unsuccessful(self):
        self.voice_recording_window.display_error("Voice didn't match. Try recording again.")


    def get_cameras_list(self):
        return VideoManager.list_cameras()
    

    def run_video_capture_window(self):
        if self.video_capture_window is None or not self.video_capture_window.winfo_exists():
            cameras_list = self.get_cameras_list()
            if self.client.status == Status.SIGNING_IN or self.client.status == Status.NORMAL:
                is_setup = True
            else:
                is_setup = False
            self.video_capture_window = VideoCaptureWindow(self, cameras_list, is_setup)
        else:
            self.video_capture_window.focus()
    
    def start_video_recording(self, camera_index):
        if self.cap is not None:
            if self.current_camera_index == camera_index:
                return
            else:
                self.cap.release()
                self.cap = None

        self.cap = VideoManager.get_cap(camera_index)
        if self.cap is None:
            self.video_capture_window.display_camera_error()
        else:
            self.current_camera_index = camera_index
            self.video_capture_window.record_loop()
            self.video_capture_window.face_recognition_loop()

    def get_frames(self):
        data = VideoManager.get_frame(self.cap)
        if data[0]:
            rgb_mirrored_frame = data[1]
            self.rgb_small_frame = data[2]
            if self.video_capture_window is not None:
                pil_image = Image.fromarray(rgb_mirrored_frame)
                image = ctk.CTkImage(light_image= pil_image, dark_image= pil_image, size= (640, 480))
                self.video_capture_window.update_frame(image)
        else:
            self.video_capture_window.display_camera_error()

    def call_face_recognition(self):
        if self.rgb_small_frame is not None:
            self.client.get_face_encoding(self.rgb_small_frame)
        else:
            self.video_capture_window.disable_setup_button()
    
    def face_located(self):
        self.video_capture_window.enable_setup_button()

    def no_face_located(self):
        self.video_capture_window.disable_setup_button()

    def call_setup_face_recognition(self):
        self.client.setup_face_recognition()

    def face_recognition_setup_successful(self):
        self.video_capture_window.close_window()
        if self.client.status == Status.SIGNING_IN:
            self.signup_window.face_recognition_added()
        elif self.client.status == Status.NORMAL:
            self.settings_menu.face_recognition_added()

    def face_recognition_successful(self):
        self.video_capture_window.close_window()
        self.auth_successful()

    def face_recognition_unsuccessful(self):
        self.video_capture_window.display_face_recognition_error("Face doesn't match.")

    def auth_successful(self):
        username = self.client.username
        if self.client.status == Status.LOGGING_IN:
            self.setup_user(username)
        elif self.client.status == Status.RECOVERING_PASSWORD:
            self.run_reset_password_window()

    def get_registered_sites(self):
        return self.client.get_registered_sites(False)
    
    def get_deleted_sites(self):
        return self.client.get_registered_sites(True)

    def setup_user(self, username):
        self.login_button.place_forget()
        self.signup_button.place_forget()

        self.username_text.configure(text= username)
        self.username_text.place(x= 900, y= 75)
        self.register_site_button.place(x= 150, y= 150)
        self.site_info_button.place(x= 350, y= 150)
        self.change_password_button.place(x= 550, y= 150)
        self.delete_site_button.place(x= 750, y= 150)
        self.recover_site_button.place(x= 950, y= 150)

        self.load_registered_sites()
        self.search_box.place(x= 100, y= 220)
        self.delete_search_button.place(x= 1050, y= 220)
        self.registered_sites_list.place(x= 100, y= 250)

        self.settings_menu = SettingsMenuFrame(self, WINDOW_WIDTH, self.client.auth_options, corner_radius = 0)
        self.settings_menu.place(relx=1.0, rely=0, relheight=1, anchor="nw")

        self.settings_button = ctk.CTkButton(self.window, width= 40, text= "⚙", text_color= "black", fg_color= "transparent", command= self.settings_menu.toggle)
        self.settings_button.place(x=1150, y=10)

        self.client.change_status(Status.NORMAL)

    def run_site_registration_window(self):
        if self.site_registration_window is None or not self.site_registration_window.winfo_exists():
            self.site_registration_window = SiteRegistrationWindow(self)
            self.client.change_status(Status.REGISTERING_SITE)
        else:
            self.site_registration_window.focus()

    def call_register_site(self, site_url, site_username, password_preferences):
        self.client.register_site(site_url, site_username, password_preferences)

    def display_registration_error(self, msg):
        self.site_registration_window.display_registration_error(msg)

    def registration_succesful(self, password):
        copy_password = self.site_registration_window.close_window()
        self.load_registered_sites()
        if copy_password:
            self.copy_to_clipboard(password)
        self.client.change_status(Status.NORMAL)

    def run_password_preferences_window(self, preferences = None, site_url = None):
        if self.password_preferences_window is None or not self.password_preferences_window.winfo_exists():
            self.password_preferences_window = PasswordPreferencesWindow(self, preferences, site_url)
            self.password_preferences_window.focus()
            self.password_preferences_window.lift()
        else:
            self.password_preferences_window.focus()
            self.password_preferences_window.lift()

    def save_password_preferences(self, preferences, site_url):
        if self.client.status == Status.REGISTERING_SITE:
            self.site_registration_window.preferences = preferences
            self.password_preferences_window.close_window()
        elif self.client.status == Status.NORMAL:
            self.call_update_password_preferences(site_url, preferences)
            self.password_preferences_window.close_window()

    def load_registered_sites(self, *args):
        self.registered_sites_list.delete("all")
        registered_sites = self.get_registered_sites()
        found_current_selection = False
        for site_url in registered_sites:
            if self.search_var.get() != "":
                if self.search_var.get().lower() in site_url.lower():
                    self.registered_sites_list.insert("end", site_url)
                    if site_url == self.curret_site_selection:
                        found_current_selection = True
                        self.registered_sites_list.select(-1)
            else:
                self.registered_sites_list.insert("end", site_url)
                if site_url == self.curret_site_selection:
                        found_current_selection = True
                        self.registered_sites_list.select(-1)
        
        if not found_current_selection:
            self.disable_site_buttons()

    def enable_site_buttons(self, site):
        self.curret_site_selection = site
        self.site_info_button.configure(state= "normal")
        self.change_password_button.configure(state= "normal")
        self.delete_site_button.configure(state= "normal")

    def disable_site_buttons(self):
        self.current_site_selection = None
        self.site_info_button.configure(state= "disabled")
        self.change_password_button.configure(state= "disabled")
        self.delete_site_button.configure(state= "disabled")


    def show_selected_site_info(self):
        site_url = self.registered_sites_list.get()
        site_username, site_password = self.call_site_info(site_url)
        self.run_site_info_window(site_username, site_password)

    def call_site_info(self, site_url):
        return self.client.get_site_info(site_url)
    
    def run_site_info_window(self, site_username, site_password):
        if self.site_info_window is None or not self.site_info_window.winfo_exists():
            self.site_info_window = SiteInfoWindow(self, site_username, site_password)
        else:
            self.site_info_window.focus()

    def initiate_change_password_window(self):
        site_url = self.registered_sites_list.get()
        site_username, site_password = self.call_site_info(site_url)
        self.run_change_site_password_window(site_url, site_username)
        
    def run_change_site_password_window(self, site_url, site_username):
        if self.change_password_window is None or not self.change_password_window.winfo_exists():
            self.change_password_window = ChangePasswordWindow(self, site_url, site_username)
        else:
            self.change_password_window.focus()

    def call_change_site_password(self, site_url):
        generated_password = self.client.change_password(site_url)
        should_copy_password = self.change_password_window.close_window()
        if should_copy_password:
            self.copy_to_clipboard(generated_password)

    def get_preferences_and_initiate_window(self, site_url):
        password_preferences = self.client.get_password_preferences(site_url)
        self.run_password_preferences_window(password_preferences, site_url)
    
    def call_update_password_preferences(self, site_url, preferences):
        self.client.update_password_preferences(site_url, preferences)

    def delete_site(self):
        site_url = self.registered_sites_list.get()
        self.client.delete_site(site_url)

    def run_site_recovery_window(self):
        deleted_sites = self.get_deleted_sites()
        if self.site_recovery_window is None or not self.site_recovery_window.winfo_exists():
            self.site_recovery_window = SiteRecoveryWindow(self, deleted_sites)
        else:
            self.site_recovery_window.focus()

    def site_recovery_successful(self):
        self.site_recovery_window.close_window()
        self.load_registered_sites()

    def call_recover_site(self, site_url):
        self.client.recover_site(site_url)

    def copy_to_clipboard(self, text):
        self.window.clipboard_clear()
        self.window.clipboard_append(text) 
        self.window.update()