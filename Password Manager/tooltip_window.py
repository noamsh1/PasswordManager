import customtkinter as ctk
from color_palettes import palette_color

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.after_id = None

        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event = None):
        x = event.x_root
        y = event.y_root + 10
        self.after_id = self.widget.after(500, lambda: self._create_tooltip(x, y))

    def _create_tooltip(self, x, y):
        if self.tip_window or not self.text:
            return
    

        self.tip_window = ctk.CTkToplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(self.tip_window, text=self.text, justify="left", fg_color=palette_color("surface"), text_color=palette_color("text"), corner_radius=10, padx=8, pady=4)
        label.pack()

    def hide_tooltip(self, *args):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None