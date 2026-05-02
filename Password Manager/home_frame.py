import customtkinter as ctk
from color_palettes import palette_color


class HomeFrame(ctk.CTkFrame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        # Large icon circle
        home_icon = ctk.CTkFrame(self, width=90, height=90, corner_radius=45, fg_color=palette_color("accent"))
        home_icon.place(relx=0.5, y=130, anchor="center")
        home_icon_lbl = ctk.CTkLabel(home_icon, width=0, height=0, text="🔒", fg_color="transparent", text_color=palette_color("surface"), font=("Segoe UI Emoji", 32))
        home_icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        home_title = ctk.CTkLabel(self, text="Secure Password Manager", font=("sans", 32, "bold"), text_color=palette_color("text"))
        home_title.place(relx=0.5, y=200, anchor="center")

        home_subtitle = ctk.CTkLabel(self, text="Keep all your credentials safe with multi-factor authentication", font=("sans", 14), text_color=palette_color("text_dim"))
        home_subtitle.place(relx=0.5, y=240, anchor="center")

        # Feature cards
        features = [
            ("🔐", "Multi-Factor Auth"),
            ("🎤", "Voice Recognition"),
            ("📷", "Face ID"),
            ("❓", "Security Questions"),
        ]
        card_w, card_h = 170, 80

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.place(relx=0.5, y=290, anchor="n")

        for icon, label in features:
            card = ctk.CTkFrame(cards_frame, width=card_w, height=card_h, corner_radius=12, fg_color=palette_color("surface"), border_width=1, border_color=palette_color("input_border"))
            card.pack(side="left", padx=10)
            card_icon = ctk.CTkLabel(card, width=0, height=0, text=icon, fg_color="transparent", font=("Segoe UI Emoji", 20))
            card_icon.place(relx=0.5, rely=0.35, anchor="center")
            card_lbl = ctk.CTkLabel(card, width=0, height=0, text=label, font=("sans", 12), text_color=palette_color("text_dim"))
            card_lbl.place(relx=0.5, rely=0.72, anchor="center")
