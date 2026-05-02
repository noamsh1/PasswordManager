import customtkinter as ctk
import threading
from color_palettes import palette_color
from tooltip_window import ToolTip

WINDOW_WIDTH = 520
WINDOW_HEIGHT = 750

class SignupWindow(ctk.CTkToplevel):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")
        self.configure(fg_color=palette_color("surface"))

        # ── Icon circle ──
        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=38, anchor="center")
        self.icon_label = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="👤", fg_color="transparent", text_color=palette_color("surface"), font=("Segoe UI Emoji", 22))
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self, anchor="center", text="Create Account", font=("sans", 26, "bold"), text_color=palette_color("text"))
        self.title_label.place(relx=0.5, y=85, anchor="center")

        # ── Main content frame ──
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.place(relx=0.5, y=108, anchor="n")
        content.columnconfigure(0, weight=1, minsize=WINDOW_WIDTH - 40)

        # ── ACCOUNT DETAILS section ──
        self.section_account = ctk.CTkLabel(content, height=18, anchor="w", text="ACCOUNT DETAILS", font=("sans", 11, "bold"), text_color=palette_color("accent"))
        self.section_account.grid(row=0, column=0, sticky="w")
        self.divider_account = ctk.CTkFrame(content, height=2, fg_color=palette_color("divider"))
        self.divider_account.grid(row=1, column=0, sticky="ew", pady=(1, 6))

        account_frame = ctk.CTkFrame(content, fg_color="transparent")
        account_frame.grid(row=2, column=0, sticky="ew")
        account_frame.columnconfigure(0, weight=1)

        self.username_label = ctk.CTkLabel(account_frame, height=18, anchor="w", text="Username", font=("sans", 13), text_color=palette_color("text_dim"))
        self.username_label.grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.username_entry = ctk.CTkEntry(account_frame, height=36, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text="Enter username", placeholder_text_color=palette_color("placeholder"), font=("sans", 14))
        self.username_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        self.password_label = ctk.CTkLabel(account_frame, height=18, anchor="w", text="Password", font=("sans", 13), text_color=palette_color("text_dim"))
        self.password_label.grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.password_entry = ctk.CTkEntry(account_frame, height=36, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text="Enter password", placeholder_text_color=palette_color("placeholder"), font=("sans", 14), show="•")
        self.password_entry.grid(row=3, column=0, sticky="ew", pady=(0, 6))
        ToolTip(self.password_entry, "Strong password requirements:\n- At least 8 characters\n- One uppercase letter\n- One lowercase letter\n- One digit\n- One special character")
        self.show_password_button = ctk.CTkButton(account_frame, width=42, height=36, corner_radius=10, fg_color=palette_color("surface2"), hover_color=palette_color("input_border"), text="\uE7B3", font=("Segoe MDL2 Assets", 16), text_color=palette_color("text"), command=lambda: self.show_password(1))
        self.show_password_button.grid(row=3, column=1, padx=(6, 0), pady=(0, 6))

        self.password_label_2 = ctk.CTkLabel(account_frame, height=18, anchor="w", text="Confirm Password", font=("sans", 13), text_color=palette_color("text_dim"))
        self.password_label_2.grid(row=4, column=0, sticky="w", pady=(0, 2))
        self.password_entry_2 = ctk.CTkEntry(account_frame, height=36, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text="Re-enter password", placeholder_text_color=palette_color("placeholder"), font=("sans", 14), show="•")
        self.password_entry_2.grid(row=5, column=0, sticky="ew")
        self.show_password_button_2 = ctk.CTkButton(account_frame, width=42, height=36, corner_radius=10, fg_color=palette_color("surface2"), hover_color=palette_color("input_border"), text="\uE7B3", font=("Segoe MDL2 Assets", 16), text_color=palette_color("text"), command=lambda: self.show_password(2))
        self.show_password_button_2.grid(row=5, column=1, padx=(6, 0))

        # ── CONTACT INFORMATION section ──
        self.section_contact = ctk.CTkLabel(content, height=18, anchor="w", text="CONTACT INFORMATION", font=("sans", 11, "bold"), text_color=palette_color("accent"))
        self.section_contact.grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.divider_contact = ctk.CTkFrame(content, height=2, fg_color=palette_color("divider"))
        self.divider_contact.grid(row=4, column=0, sticky="ew", pady=(1, 6))

        contact_frame = ctk.CTkFrame(content, fg_color="transparent")
        contact_frame.grid(row=5, column=0, sticky="ew")
        contact_frame.columnconfigure(0, weight=1)

        self.email_label = ctk.CTkLabel(contact_frame, height=18, anchor="w", text="Email", font=("sans", 13), text_color=palette_color("text_dim"))
        self.email_label.grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.email_var = ctk.StringVar()
        self.email_var.trace_add("write", self.on_email_entry_changed)
        self.email_entry = ctk.CTkEntry(contact_frame, textvariable=self.email_var, height=36, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text="Enter email", placeholder_text_color=palette_color("placeholder"), font=("sans", 14))
        self.email_entry.grid(row=1, column=0, sticky="ew")
        self.email_debounce_timer = None
        self.verify_email_button = ctk.CTkButton(contact_frame, width=80, height=36, corner_radius=10, fg_color=palette_color("surface2"), hover_color=palette_color("input_border"), text="Verify", text_color=palette_color("text"), border_width=2, border_color=palette_color("surface2"), font=("sans", 13), state="disabled", command=self.call_email_verification)
        self.verify_email_button.grid(row=1, column=1, padx=(6, 0))

        # ── SECURITY QUESTIONS section ──
        self.section_questions = ctk.CTkLabel(content, height=18, anchor="w", text="SECURITY QUESTIONS", font=("sans", 11, "bold"), text_color=palette_color("accent"))
        self.section_questions.grid(row=6, column=0, sticky="w", pady=(10, 0))
        self.divider_questions = ctk.CTkFrame(content, height=2, fg_color=palette_color("divider"))
        self.divider_questions.grid(row=7, column=0, sticky="ew", pady=(1, 6))

        self.security_questions_row = self._make_option_row(content, 56, "❓", "Setup Security Questions", "Required for account recovery", self.call_setup_security_questions_window)
        self.security_questions_row.grid(row=8, column=0, sticky="ew")

        # ── ADDITIONAL SECURITY (OPTIONAL) section ──
        self.section_optional = ctk.CTkLabel(content, height=18, anchor="w", text="ADDITIONAL SECURITY (OPTIONAL)", font=("sans", 11, "bold"), text_color=palette_color("accent"))
        self.section_optional.grid(row=9, column=0, sticky="w", pady=(10, 0))
        self.divider_optional = ctk.CTkFrame(content, height=2, fg_color=palette_color("divider"))
        self.divider_optional.grid(row=10, column=0, sticky="ew", pady=(1, 6))

        self.voice_auth_row = self._make_option_row(content, 56, "🎤", "Voice Authentication", "Authenticate with your voice", self.call_run_voice_recording_window)
        self.voice_auth_row.grid(row=11, column=0, sticky="ew", pady=(0, 6))

        self.face_recognition_row = self._make_option_row(content, 56, "📷", "Face Recognition", "Authenticate with your face", self.call_run_video_capture_window)
        self.face_recognition_row.grid(row=12, column=0, sticky="ew")

        # ── Create Account button ──
        self.signup_button = ctk.CTkButton(content, height=38, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Create Account", text_color=palette_color("surface"), font=("sans", 14), state="disabled", command=self.call_signup)
        self.signup_button.grid(row=13, column=0, sticky="ew", pady=(12, 0))

        self.error_text = ctk.CTkLabel(content, anchor="center", text="", font=("sans", 16), text_color=palette_color("error"))
        self.error_text.grid(row=14, column=0, pady=(6, 0))

        self.transient(app.window)
        self.lift()

    def _make_option_row(self, parent, h, icon, title, desc, command):
        bg = palette_color("surface2")
        border = palette_color("input_border")
        text_col = palette_color("text")
        dim_col = palette_color("text_dim")
        hover_bg = palette_color("input_border")

        frame = ctk.CTkFrame(parent, height=h, corner_radius=10, fg_color=bg, border_color=border, border_width=2)
        icon_lbl = ctk.CTkLabel(frame, text=icon, font=("Segoe UI Emoji", 18), text_color=text_col, fg_color="transparent")
        icon_lbl.place(x=24, rely=0.5, anchor="center")
        title_lbl = ctk.CTkLabel(frame, text=title, font=("sans", 14, "bold"), text_color=text_col, fg_color="transparent")
        title_lbl.place(x=46, rely=0.28, anchor="w")
        desc_lbl = ctk.CTkLabel(frame, height=0, text=desc, font=("sans", 11), text_color=dim_col, fg_color="transparent")
        desc_lbl.place(x=46, rely=0.66, anchor="w")

        for widget in [frame, icon_lbl, title_lbl, desc_lbl]:
            widget.bind("<Enter>", lambda e, f=frame: f.configure(fg_color=hover_bg))
            widget.bind("<Leave>", lambda e, f=frame: f.configure(fg_color=bg))
            widget.bind("<Button-1>", lambda e, cmd=command: cmd())

        return frame

    def can_signup(self):
        self.signup_button.configure(state="normal")

    def show_password(self, num):
        if num == 1:
            self.password_entry.configure(show="")
            self.show_password_button.configure(text="\uED1A", command=lambda: self.hide_password(1))
        elif num == 2:
            self.password_entry_2.configure(show="")
            self.show_password_button_2.configure(text="\uED1A", command=lambda: self.hide_password(2))

    def hide_password(self, num):
        if num == 1:
            self.password_entry.configure(show="•")
            self.show_password_button.configure(text="\uE7B3", command=lambda: self.show_password(1))
        elif num == 2:
            self.password_entry_2.configure(show="•")
            self.show_password_button_2.configure(text="\uE7B3", command=lambda: self.show_password(2))

    def call_signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        password_2= self.password_entry_2.get()
        email = self.email_entry.get()
        if password != password_2:
            self.display_signup_error("Passwords do not match")
        else:
            self.app.call_signup(username, password, email)

    def on_email_entry_changed(self, *args):
        self.email_entry.configure(border_color=palette_color("input_border"))
        if self.email_debounce_timer:
            self.after_cancel(self.email_debounce_timer)
        self.email_debounce_timer = self.after(500, self.check_email_validity)

    def check_email_validity(self):
        email = self.email_entry.get()
        self.verify_email_button.configure(state="disabled", border_color=palette_color("surface2"))
        self.email_entry.configure(border_color=palette_color("warning"))
        thread = threading.Thread(target = self.app.call_is_email_valid, args = (email, ))
        thread.start()

    def email_valid(self):
        self.email_entry.configure(border_color=palette_color("success"))
        self.verify_email_button.configure(state="normal")

    def email_invalid(self):
        self.email_entry.configure(border_color=palette_color("error"))

    def call_email_verification(self):
        email = self.email_entry.get()
        self.app.request_login_code(email)

    def email_verified(self):
        self.verify_email_button.configure(state="disabled", border_color=palette_color("success"))

    def call_run_voice_recording_window(self):
        self.app.run_voice_recording_window()

    def voice_auth_added(self):
        self.voice_auth_row.configure(border_color=palette_color("accent"))

    def call_run_video_capture_window(self):
        self.app.run_video_capture_window()

    def face_recognition_added(self):
        self.face_recognition_row.configure(border_color=palette_color("accent"))

    def call_setup_security_questions_window(self):
        self.app.run_security_questions_setup_window()

    def questions_setup_successful(self):
        self.security_questions_row.configure(border_color=palette_color("accent"))

    def display_signup_error(self, msg):
        self.error_text.configure(text=msg)

    def close_window(self):
        self.destroy()