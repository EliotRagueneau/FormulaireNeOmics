from tkinter.font import *

from py2neo import Graph

from Colors import *
from ScrollingFrame import ScrollingFrame
from tkentrycomplete import AutocompleteCombobox

graph = Graph("bolt://3.90.85.77:33014", auth=("neo4j", "dye-color-compressions"))

font = Font(family="Roboto", size=10)

root.title("Cypher Query Creator")
root.configure(bg=BG_COLOR)

try:
    root.wm_title("Cypher Query Creator")
    root.wm_iconbitmap("icon.ico")
except:
    pass

line_width = 250

test = tk.Frame(root)
test.pack()
work_frame = ScrollingFrame(test, root)
work_frame.pack(expand=True)
line_frame = tk.Frame(work_frame.frame, relief='flat', bg=BG_COLOR)
line_frame.pack()


class Line:
    analysisLines = []
    analysis_options = [result["analysis"] for result in graph.run("MATCH (a:Analysis) RETURN a.name AS analysis")]

    def __init__(self):
        Line.analysisLines.append(self)

        self.frame = tk.Frame(line_frame, relief='flat', bg=BG_COLOR)
        self.frame.pack(anchor='w', padx=15)
        self.name = tk.Label(self.frame)
        self.name.grid(row=0, column=0)
        Line.update_line_numbers()

        self.analysis = tk.StringVar()
        self.analysis_box = AutocompleteCombobox(self.frame, textvariable=self.analysis, width=20, cursor="hand2",
                                                 font=font)
        self.analysis_box.grid(row=0, column=1)
        self.analysis_box.set_completion_list(Line.analysis_options)

        self.remove_btn = tk.Button(self.frame, image=REMOVE_ICON, relief='flat', command=self.remove_line, bg=BG_COLOR,
                                    cursor="hand2", highlightthickness=0, bd=0, activebackground=BG_COLOR)
        self.remove_btn.grid(row=0, column=2)

    @staticmethod
    def update_line_numbers():
        n = 0
        for line in Line.analysisLines:
            n += 1
            line.name.configure(text="Method {}: ".format(n))

    def remove_line(self):
        self.frame.destroy()
        Line.analysisLines.remove(self)
        Line.update_line_numbers()

    @staticmethod
    def new_line():
        Line()
        work_frame.on_frame_configure()
        work_frame.after(50, lambda: work_frame.scroll_to_end())


add_button = tk.Button(work_frame.frame, image=ADD_ICON, relief='flat', command=Line.new_line, bg=BG_COLOR,
                       cursor="hand2", highlightthickness=0, bd=0, activebackground=BG_COLOR)
add_button.pack()

Line.new_line()
root.mainloop()
