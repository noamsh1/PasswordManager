import customtkinter as ctk
from color_palettes import palette_color

WINDOW_WIDTH = 440
WINDOW_HEIGHT = 420
CODE_LENGTH = 8

class CodeLoginWindow(ctk.CTkToplevel):

    def __init__(self, app, email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app    # Reference to the UI instance
        self.client_email = email    # Email address the code was sent to

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")
        self.configure(fg_color=palette_color("surface"))

        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=45, anchor="center")
        self.icon = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="📧", fg_color="transparent", text_color=palette_color("surface"), font=("Segoe UI Emoji", 22))
        self.icon.place(relx=0.5, rely=0.5, anchor="center")

        self.title = ctk.CTkLabel(self, anchor="center", text="Enter Verification Code", font=("sans", 24, "bold"), text_color=palette_color("text"))
        self.title.place(relx=0.5, y=95, anchor="center")
        self.subtitle = ctk.CTkLabel(self, anchor="center", text=f"A code was sent to {email}", font=("sans", 13), text_color=palette_color("text_dim"))
        self.subtitle.place(relx=0.5, y=122, anchor="center")

        self.entries_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entries_frame.place(relx=0.5, y=170, anchor="n")
        self.entries = []
        for i in range(CODE_LENGTH):
            entry = ctk.CTkEntry(self.entries_frame, width=40, height=50, corner_radius=8, justify="center", font=("sans", 20, "bold"), fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"))
            entry.grid(row=0, column=i, padx=4, pady=10)
            entry.bind("<KeyPress>", lambda event, index=i: self._handle_keypress(event, index))
            self.entries.append(entry)

        self.enter_code_button = ctk.CTkButton(self, width=380, height=44, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Verify Code", text_color=palette_color("surface"), font=("sans", 16), command=self.call_check_code)
        self.enter_code_button.place(relx=0.5, y=285, anchor="center")

        self.resend_code_button = ctk.CTkButton(self, width=120, height=28, text="Resend code", text_color=palette_color("text_dim"), fg_color=palette_color("surface"), hover_color=palette_color("surface"), font=("sans", 13), state="disabled", command=self.call_resend_code)
        self.resend_code_button.bind("<Enter>", lambda e: self.resend_code_button.configure(text_color=palette_color("accent")))
        self.resend_code_button.bind("<Leave>", lambda e: self.resend_code_button.configure(text_color=palette_color("text_dim")))
        self.resend_code_button.place(relx=0.5, y=325, anchor="center")

        self.msg_text = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 14), text_color=palette_color("error"))
        self.msg_text.place(relx=0.5, y=365, anchor="center")

        self.grab_set()

    def _handle_keypress(self, event, index):
        current_entry = self.entries[index]
        content = current_entry.get()
        char = event.char
        key = event.keysym

        if key == "BackSpace":
            if content != "":
                current_entry.delete(0, "end")
            else:
                self.after(1, lambda : self._focus_back(index))
        
        if char.isdigit():
            self.after(1, lambda : self._focus_next(index))
        
        else:
            current_entry.delete(0, "end")
    
    def _focus_next(self, index):
        current_entry = self.entries[index]
        content = current_entry.get()
        if len(content) > 1:
            current_entry.delete(0, "end")
            current_entry.insert(0, content[-1])

        if index < CODE_LENGTH - 1:
            self.entries[index + 1].focus()

    def _focus_back(self, index):
        if index > 0:
            self.entries[index - 1].focus()

    def get_full_code(self):
        """Returns the full code string by concatenating all entry fields."""
        return "".join(e.get() for e in self.entries)
    
    def call_check_code(self):
        """Sends the entered code to the app for verification."""
        code = self.get_full_code()
        self.app.call_check_code(code)

    def incorrect_code_feedback(self):
        """Displays an incorrect code error and highlights the entry fields."""
        self.msg_text.configure(text="Code Incorrect")
        for entry in self.entries:
            entry.configure(border_color=palette_color("error"), border_width=3)

    def display_code_expired_msg(self):
        """Displays a code expired error, clears the entries, and enables the resend button."""
        self.display_error("Code Expired! Request another code.")
        for entry in self.entries:
            entry.delete(0, "end")
        self.resend_code_button.configure(state="normal")

    def display_error(self, msg):
        """Displays an error message."""
        self.msg_text.configure(text=msg, text_color=palette_color("error"))

    def display_msg(self, msg):
        """Displays an informational message."""
        self.msg_text.configure(text=msg, text_color=palette_color("text"))

    def call_resend_code(self):
        """Requests a new verification code via the app."""
        self.app.request_login_code(self.client_email)

    def code_resent(self):
        """Displays a confirmation message and disables the resend button."""
        self.display_msg("Code Sent")
        self.resend_code_button.configure(state="disabled")

    def close_window(self):
        """Destroys the window."""
        self.destroy()