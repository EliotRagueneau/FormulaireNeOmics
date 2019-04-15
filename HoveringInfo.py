from tkinter import *

class HoverInfo(Label):
    def __init__(self, parent, text):
        Label.__init__(self, parent, text=text)
        if not isinstance(text, str):
            raise TypeError('Trying to initialise a Hover Menu with a non string type: ' + text.__class__.__name__)
        self._displayed = False
        self.master.bind("<Enter>", self.Display)
        self.master.bind("<Leave>", self.Remove)

    def __del__(self):
        self.master.unbind("<Enter>")
        self.master.unbind("<Leave>")

    def Display(self, event):
        if not self._displayed:
            self._displayed = True

    def Remove(self, event):
        if self._displayed:
            self._displayed = False