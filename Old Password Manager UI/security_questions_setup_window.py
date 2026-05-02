import customtkinter as ctk

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 420


class SecurityQuestionsSetupWindow(ctk.CTkToplevel):

    def __init__(self, app, security_questions, answers_dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Setup Security Questions", font= ("sans", 44), text_color= "black")
        self.title.place(x= 500, y= 25, anchor= "center")

        self.instructions_label = ctk.CTkLabel(self, anchor= "center", text= "Choose 3 security questions and answer them", font= ("sans", 22), text_color= "black")
        self.instructions_label.place(x= 500, y= 75, anchor= "center")

        self.setup_questions_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Setup Security Questions", text_color= "black", border_color= "green", state= "disabled", command= self.setup_security_questions)
        self.setup_questions_button.place(x = 500, y= 360, anchor= "center")

        self.questions_frame = ctk.CTkScrollableFrame(self, width= 980, height= 200, border_color= "blue", scrollbar_button_color= "blue", scrollbar_button_hover_color= "cyan")
        self.questions_frame.place(x= 0, y= 110)

        self.security_questions = security_questions
        self.check_vars = []
        self.questions_entries = []

        for i in range(len(security_questions)):
            question = security_questions[i]
            var = ctk.BooleanVar(value= False)
            cb = ctk.CTkCheckBox(self.questions_frame, height= 30, corner_radius= 2, border_color= "blue", checkmark_color= "dark green", text= question, font= ("sans", 18), variable= var, command= lambda i = i: self.on_checkbox(i))
            cb.grid(column= 0, row= i, sticky= "W")
            self.check_vars.append(var)
            entry = ctk.CTkEntry(self.questions_frame, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
            self.questions_entries.append(entry)
            if answers_dict is not None:
                if i in answers_dict.keys():
                    var.set(True)
                    self.on_checkbox(i)
                    entry.insert(0, answers_dict[i])
        

        self.error_text = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 25), text_color= "red")
        self.error_text.place(x= 500, y= 400, anchor= "center")

        self.grab_set()


    def on_checkbox(self, i):
        ticked_checkboxes_count = sum(var.get() for var in self.check_vars)
        entry = self.questions_entries[i]
        if self.check_vars[i].get():
            if ticked_checkboxes_count > 3:
                self.check_vars[i].set(False)
            else:
                entry.grid(column= 1, row= i, padx = 20, sticky= "W")
                if ticked_checkboxes_count == 3:
                    self.setup_questions_button.configure(state= "normal")
        else:
            entry.grid_forget()
            self.setup_questions_button.configure(state= "disabled")

    def setup_security_questions(self):
        chosen_questions_dict = {}
        for i in range(len(self.check_vars)):
            if self.check_vars[i].get():
                user_answer = self.questions_entries[i].get()
                if user_answer == "":
                    self.display_error("You must answer the questions you have picked")
                else:
                    # sqlite autoincrement starts at 1
                    chosen_questions_dict[i + 1] = user_answer.lower().strip()
        self.app.call_setup_security_questions(chosen_questions_dict)


    def display_error(self, msg):
        self.error_text.configure(text= msg)

    def close_window(self):
        self.destroy()

# window = SecurityQuestionsSetupWindow(None, SECURITY_QUESTIONS_LIST).mainloop()