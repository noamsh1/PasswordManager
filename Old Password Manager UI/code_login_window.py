import customtkinter as ctk

WINDOW_WIDTH = 710
WINDOW_HEIGHT = 400
CODE_LENGTH = 8

class CodeLoginWindow(ctk.CTkToplevel):

    def __init__(self, app, email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.client_email = email

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.wm_title("Password Manager")

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Login With Code", font= ("sans", 50), text_color= "black")
        self.title.place(x= 355, y= 25, anchor= "center")

        self.entries_frame = ctk.CTkFrame(self, width = 500, height = 100)
        self.entries_frame.place(x = 175, y = 150)
        self.entries = []
        for i in range(CODE_LENGTH):
            entry = ctk.CTkEntry(self.entries_frame, width = 40, height=50, justify="center", font=("sans", 20))
            entry.grid(row = 0, column = i, padx = 10, pady = 20)
            entry.bind("<KeyPress>", lambda event, index = i: self._handle_keypress(event, index))
            self.entries.append(entry)

        self.enter_code_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Enter Code", text_color= "black", border_color= "green", command = self.call_check_code)
        self.enter_code_button.place(x = 340, y = 300)

        self.resend_code_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Resend Code", text_color= "black", border_color= "green", state = "disabled", command = self.call_resend_code)
        self.resend_code_button.place(x = 500, y = 300)

        self.msg_text = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 20), text_color= "red")
        self.msg_text.place(x = 355, y = 360, anchor= "center")
        
        self.transient(self.app.window)
        self.lift()

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
        return "".join(e.get() for e in self.entries)
    
    def call_check_code(self):
        code = self.get_full_code()
        self.app.call_check_code(code)

    def incorrect_code_feedback(self):
        self.msg_text.configure(text= "Code Incorrect")
        for entry in self.entries:
            entry.configure(border_color = "red", border_width = 3)

    def display_code_expired_msg(self):
        self.display_error("Code Expired! Request another code")
        for entry in self.entries:
            entry.delete(0, "end")
        self.resend_code_button.configure(state = "normal")

    def display_error(self, msg):
        self.msg_text.configure(text= msg, text_color= "red")

    def display_msg(self, msg):
        self.msg_text.configure(text= msg, text_color= "black")

    def call_resend_code(self):
        self.app.request_login_code(self.client_email)

    def code_resent(self):
        self.display_msg("Code Sent")
        self.resend_code_button.configure(state= "disabled")

    def close_window(self):
        self.destroy()