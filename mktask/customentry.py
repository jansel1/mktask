import tkinter as tk

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.default_fg_color = self.cget("foreground")
        self.placeholder_fg_color = "grey"
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.insert(0, self.placeholder)
        self.config(foreground=self.placeholder_fg_color)


    def _on_focus_in(self, event): # for placeholder entries
        if self.get() == self.placeholder:
            self.config(foreground=self.default_fg_color)
            self.delete(0, tk.END)

    def _on_focus_out(self, event):
        if not self.get():
            self.config(foreground=self.placeholder_fg_color)
            self.insert(0, self.placeholder)

