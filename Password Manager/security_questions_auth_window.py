import customtkinter as ctk
from color_palettes import palette_color

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 520


class SecurityQuestionsAuthWindow(ctk.CTkToplevel):

    def __init__(self, app, user_security_questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)
        self.configure(fg_color=palette_color("surface"))

        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("btn_auth"))
        self.icon_circle.place(relx=0.5, y=45, anchor="center")
        self.icon = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="🛡", fg_color="transparent", text_color=palette_color("surface"), font=("sans", 20))
        self.icon.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self, anchor="center", text="Security Verification", font=("sans", 26, "bold"), text_color=palette_color("text"))
        self.title_label.place(relx=0.5, y=95, anchor="center")

        self.subtitle = ctk.CTkLabel(self, anchor="center", text="Answer your security questions to continue", font=("sans", 13), text_color=palette_color("text_dim"))
        self.subtitle.place(relx=0.5, y=125, anchor="center")

        self.user_security_questions = user_security_questions
        self.answers_entries = []

        self.questions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.questions_frame.place(x=30, y=150, relwidth=0.87)
        self.questions_frame.columnconfigure(1, weight=1)

        for i in range(len(user_security_questions)):
            question = self.user_security_questions[i]
            row = i * 2
            num_circle = ctk.CTkFrame(self.questions_frame, width=26, height=26, corner_radius=13, fg_color=palette_color("accent"))
            num_circle.pack_propagate(False)
            num_circle.grid(row=row, column=0, sticky="w", padx=(0, 8))
            num_label = ctk.CTkLabel(num_circle, width=0, height=0, text=str(i + 1), fg_color="transparent", text_color=palette_color("surface"), font=("sans", 12, "bold"))
            num_label.place(relx=0.5, rely=0.5, anchor="center")
            q_label = ctk.CTkLabel(self.questions_frame, anchor="w", text=question, font=("sans", 13), text_color=palette_color("text"))
            q_label.grid(row=row, column=1, sticky="w")
            entry = ctk.CTkEntry(self.questions_frame, height=38, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text_color=palette_color("placeholder"), font=("sans", 14), placeholder_text="Type your answer...")
            self.answers_entries.append(entry)
            entry.grid(row=row + 1, column=0, columnspan=2, sticky="ew", pady=(4, 14))

        btn_row = len(user_security_questions) * 2
        self.enter_answers_button = ctk.CTkButton(self.questions_frame, height=42, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Submit Answers", text_color=palette_color("surface"), font=("sans", 14), command=self.check_answers)
        self.enter_answers_button.grid(row=btn_row, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.error_text = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 13), text_color=palette_color("error"))
        self.error_text.place(relx=0.5, rely=1.0, y=-20, anchor="center")

        self.grab_set()


    def check_answers(self):
        answers = []
        for entry in self.answers_entries:
            answer = entry.get()
            if answer == "":
                self.display_error("Answer all of the questions before submitting them")
                return
            else:
                answers.append(answer.lower().strip())
        self.app.call_check_security_answers(answers)


    def display_error(self, msg):
        self.error_text.configure(text=msg)

    def close_window(self):
        self.destroy()