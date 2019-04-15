__author__ = "Bryan Oakley"
import tkinter as tk


class ScrollingFrame(tk.Frame):
    def __init__(self,parent, root):
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(parent, borderwidth=0, background="#ffffff", highlightthickness=0, height=540)
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.on_frame_configure)

        # with Windows OS
        root.bind("<MouseWheel>", self.on_mousewheel)
        # with Linux OS
        root.bind("<Button-4>", self.on_mousewheel)
        root.bind("<Button-5>", self.on_mousewheel)

    def scroll_to_end(self):
        self.canvas.yview_moveto(1)

    def on_mousewheel(self, event=None):
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

    def on_frame_configure(self, *args):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


if __name__ == "__main__":
    root = tk.Tk()
    ScrollingFrame(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
