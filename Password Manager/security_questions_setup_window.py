import customtkinter as ctk
from color_palettes import palette_color

WINDOW_WIDTH = 520
WINDOW_HEIGHT = 580


class SecurityQuestionsSetupWindow(ctk.CTkToplevel):

    def __init__(self, app, security_questions, answers_dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app    # Reference to the UI instance

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)
        self.configure(fg_color=palette_color("surface"))

        # ── Icon circle ──
        self.icon_circle = ctk.CTkFrame(self, width=56, height=56, corner_radius=28, fg_color=palette_color("accent"))
        self.icon_circle.place(relx=0.5, y=38, anchor="center")
        self.icon_label = ctk.CTkLabel(self.icon_circle, width=0, height=0, text="❓", fg_color="transparent", text_color=palette_color("surface"), font=("Segoe UI Emoji", 22))
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self, anchor="center", text="Setup Security Questions", font=("sans", 22, "bold"), text_color=palette_color("text"))
        self.title_label.place(relx=0.5, y=85, anchor="center")

        self.subtitle = ctk.CTkLabel(self, anchor="center", text="Choose 3 questions and provide your answers", font=("sans", 13), text_color=palette_color("text_dim"))
        self.subtitle.place(relx=0.5, y=112, anchor="center")

        # ── Scrollable questions frame ──
        self.questions_frame = ctk.CTkScrollableFrame(self, width=WINDOW_WIDTH - 60, height=300, fg_color=palette_color("surface"), border_color=palette_color("input_border"), border_width=1, scrollbar_button_color=palette_color("accent"), scrollbar_button_hover_color=palette_color("accent_hover"))
        self.questions_frame.place(relx=0.5, y=135, anchor="n")
        self.questions_frame.columnconfigure(0, weight=0)
        self.questions_frame.columnconfigure(1, weight=1)

        self.security_questions = security_questions    # List of available security questions
        self.check_vars = []    # List of BooleanVar for each question checkbox
        self.questions_entries = []    # List of entry widgets for each question's answer

        for i in range(len(security_questions)):
            question = security_questions[i]
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(self.questions_frame, height=28, corner_radius=4, border_color=palette_color("input_border"), checkmark_color=palette_color("surface"), fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text=question, font=("sans", 13), text_color=palette_color("text"), variable=var, command=lambda i=i: self.on_checkbox(i))
            cb.grid(column=0, row=i * 2, columnspan=2, sticky="w", pady=(4, 0))
            self.check_vars.append(var)
            entry = ctk.CTkEntry(self.questions_frame, height=34, corner_radius=8, fg_color=palette_color("input_bg"), border_color=palette_color("input_border"), text_color=palette_color("text"), placeholder_text="Type your answer...", placeholder_text_color=palette_color("placeholder"), font=("sans", 13))
            self.questions_entries.append(entry)
            if answers_dict is not None:
                if i in answers_dict.keys():
                    var.set(True)
                    self.on_checkbox(i)
                    entry.insert(0, answers_dict[i])

        # ── Setup button ──
        self.setup_questions_button = ctk.CTkButton(self, width=WINDOW_WIDTH - 60, height=38, corner_radius=10, fg_color=palette_color("accent"), hover_color=palette_color("accent_hover"), text="Save Security Questions", text_color=palette_color("surface"), font=("sans", 14), state="disabled", command=self.setup_security_questions)
        self.setup_questions_button.place(relx=0.5, y=495, anchor="center")

        self.error_text = ctk.CTkLabel(self, anchor="center", text="", font=("sans", 14), text_color=palette_color("error"))
        self.error_text.place(relx=0.5, y=540, anchor="center")

        self.grab_set()


    def on_checkbox(self, i):
        """Shows or hides the answer entry for question i. Limits selection to 3 questions."""
        ticked_checkboxes_count = sum(var.get() for var in self.check_vars)
        entry = self.questions_entries[i]
        if self.check_vars[i].get():
            if ticked_checkboxes_count > 3:
                self.check_vars[i].set(False)
            else:
                entry.grid(column=0, row=i * 2 + 1, columnspan=2, sticky="ew", padx=(26, 0), pady=(2, 6))
                if ticked_checkboxes_count == 3:
                    self.setup_questions_button.configure(state="normal")
        else:
            entry.grid_forget()
            self.setup_questions_button.configure(state="disabled")

    def setup_security_questions(self):
        """Collects the selected questions and answers, then sends them to the app."""
        chosen_questions_dict = {}
        for i in range(len(self.check_vars)):
            if self.check_vars[i].get():
                user_answer = self.questions_entries[i].get()
                if user_answer == "":
                    self.display_error("You must answer the questions you have picked")
                    return
                else:
                    # sqlite autoincrement starts at 1
                    chosen_questions_dict[i + 1] = user_answer.lower().strip()
        self.app.call_setup_security_questions(chosen_questions_dict)


    def display_error(self, msg):
        """Displays an error message in the window."""
        self.error_text.configure(text=msg)

    def close_window(self):
        """Destroys the window."""
        self.destroy()