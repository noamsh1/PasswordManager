import customtkinter as ctk

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400


class SecurityQuestionsAuthWindow(ctk.CTkToplevel):

    def __init__(self, app, user_security_questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.wm_title("Password Manager")
        self.resizable(False, False)

        self.title = ctk.CTkLabel(self, anchor= "center", text= "Authenticate with Security Questions", font= ("sans", 44), text_color= "black")
        self.title.place(x= 400, y= 25, anchor= "center")

        self.questions_frame = ctk.CTkFrame(self, width= 800, height= 250)
        self.questions_frame.grid_propagate(False)
        self.questions_frame.place(x= 0, y= 75)

        self.user_security_questions = user_security_questions
        self.answers_entries = []

        for i in range(len(user_security_questions)):
            question = self.user_security_questions[i]
            label = ctk.CTkLabel(self.questions_frame, anchor= "center", text= question, font= ("sans", 20), text_color= "black")
            label.grid(column= 0, row= i * 2, sticky= "W", padx= 30)
            entry = ctk.CTkEntry(self.questions_frame, width= 200, height= 30, corner_radius= 5, fg_color= "light gray", border_color= "blue", text_color= "black", font= ("sans", 20))
            self.answers_entries.append(entry)
            entry.grid(column= 0, row= i * 2 + 1, pady= 10)


        self.error_text = ctk.CTkLabel(self, anchor= "center", text= "", font= ("sans", 25), text_color= "red")
        self.error_text.place(x= 400, y= 380, anchor= "center")

        self.enter_answers_button = ctk.CTkButton(self, width= 150, height= 50, corner_radius= 5, fg_color= "green", hover_color= "light green", text= "Submit answers", text_color= "black", border_color= "green", command= self.check_answers)
        self.enter_answers_button.place(x = 400, y= 350, anchor= "center")

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
        self.error_text.configure(text= msg)

    def close_window(self):
        self.destroy()

# window = SecurityQuestionsAuthWindow(None, ["What is the name of your grandmother from your father's side?", "What was the house number of the house you lived in as a child? (digits)", "What was the name of the first school you ever attended?",]).mainloop()