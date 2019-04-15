import tkinter as tk
import tkinter.ttk as ttk
from ScrollingFrame import ScrollingFrame

BG_COLOR = "white"
ACCENT_COLOR = "#A2A2A2"
FONT_CLEAR_COLOR = "white"
FONT_DARK_COLOR = "#C4C4C4"

root = tk.Tk()
root.title = "Cypher Query Creator"
root.iconbitmap = "Ressources/icon.ico"
root.configure(bg="white")

try:
    root.wm_title = "Cypher Query Creator"
    root.wm_iconbitmap = "Ressources/icon.ico"
except:
    pass

query = tk.StringVar()
query.set("MATCH")
tk.Label(root, textvariable=query, width=40, anchor='e', bg=BG_COLOR).pack()

nodes = []


def id_generator():
    for letter in "abcedfghijklmnopqrstuvwxyz":
        yield letter


def update_query(*args):
    ids = id_generator()
    matches = "MATCH "
    returned = " RETURN "
    return_sth = False
    for node in nodes:

        matches += "("
        if node.returned.get() == 1:
            node_id = next(ids)
            matches += "{}".format(node_id)
            returned += "{}, ".format(node_id)
            return_sth = True
        matches += ":{}".format(node.type)
        if node.name.get() != "":
            matches += ' {{name: "{}" }}'.format(node.name.get())
        matches += ")"

        if node.link:
            if node.link.simple:
                matches += "-"
            else:
                matches += "-[*{}..{}]-".format(node.link.min.get(), node.link.max.get())
    if return_sth:
        returned = returned[:-2]
    query.set(matches + returned)
    return matches + returned


line_width = 250
upper_line_canvas = tk.Canvas(root, borderwidth=0, bg=BG_COLOR, highlightthickness=0, height=8,
                              width=line_width)
upper_line_canvas.pack()
upper_line_canvas.create_line(0, 5, line_width, 5, fill=ACCENT_COLOR)

test = tk.Frame(root)
test.pack()
work_frame = ScrollingFrame(test, root)
work_frame.pack(expand=True)

lower_line_canvas = tk.Canvas(root, borderwidth=0, bg=BG_COLOR, highlightthickness=0, height=8,
                              width=line_width)
lower_line_canvas.pack()
lower_line_canvas.create_line(0, 5, line_width, 5, fill=ACCENT_COLOR)


# scrolling_canvas = Canvas(root, height=800, bg="white")
# scrollbar = Scrollbar(work_frame, orient="vertical", command=scrolling_canvas.yview)
# scrolling_canvas.configure(yscrollcommand=scrollbar.set)
# scrolling_canvas.pack(side="left")
# scrollbar.pack(side="right", fill="y")
# frame.bind("<Configure>", myfunction)


class Line:
    node_icon = tk.PhotoImage(file="Ressources/Unknown_node.png")
    add_icon = tk.PhotoImage(file="Ressources/Add_button.png")
    entry_bg = tk.PhotoImage(file="Ressources/Entry_bg.png")
    remove_icon = tk.PhotoImage(file="Ressources/Remove_line.png")

    def __init__(self):
        nodes.append(self)

        self.frame = tk.Frame(work_frame.frame, relief='flat', bg=BG_COLOR)
        self.frame.pack(anchor='w', padx=15)

        type_variable = tk.StringVar()

        tk.OptionMenu(self.frame, image=self.node_icon, relief='flat', bg=BG_COLOR, cursor="hand2").grid(row=0, column=0)
        self.type = ""
        self.returned = tk.IntVar()
        self.name = tk.StringVar()
        tk.Checkbutton(self.frame, variable=self.returned, text="name : ", bg=BG_COLOR).grid(row=0, column=1)
        ttk.Combobox(self.frame, textvariable=self.name, width=30, cursor="hand2").grid(row=0, column=2)

        self.name.trace('w', update_query)
        self.returned.trace('w', update_query)
        self.add_button = tk.Button(self.frame, image=self.add_icon, relief='flat', command=self.new_line, bg=BG_COLOR,
                                    cursor="hand2")
        self.add_button.grid(row=2, column=0)
        self.link = None

    def type_choice(self):
        choice_frame = tk.Frame(self.frame)
        choice_frame.grid(row=2, column=0)


    def new_line(self):
        self.add_button.grid_forget()
        self.link = Link()
        Line()
        update_query()
        work_frame.on_frame_configure()
        work_frame.after(50, lambda: work_frame.scroll_to_end())


class Link:
    simple_link_icon = tk.PhotoImage(file="Ressources/Lien.png")
    composed_link_icon = tk.PhotoImage(file="Ressources/Composed_Link.png")

    def switch(self):
        if self.simple:
            self.simple = False
            self.icon.configure(image=self.composed_link_icon)
            self.min_frame.grid()
            self.middle_frame.grid()
            self.max_frame.grid()
        else:
            self.simple = True
            self.icon.configure(image=self.simple_link_icon)
            self.min_frame.grid_remove()
            self.middle_frame.grid_remove()
            self.max_frame.grid_remove()
        update_query()

    def update_max(self):
        if self.max.get() < self.min.get():
            self.max.set(self.min.get())

    def update_min(self):
        if self.max.get() < self.min.get():
            self.min.set(self.max.get())

    def __init__(self):
        self.simple = True
        self.frame = tk.Frame(work_frame.frame, bg=BG_COLOR)
        self.frame.pack(anchor='w', padx=45)
        self.icon = tk.Button(self.frame, relief='flat', image=self.simple_link_icon, command=self.switch, bg=BG_COLOR,
                              cursor="hand2")
        self.icon.grid(row=0, column=0)
        self.min = tk.IntVar()
        self.max = tk.IntVar()

        self.min_frame = tk.Frame(self.frame, bg=BG_COLOR)
        self.middle_frame = tk.Frame(self.frame, bg=BG_COLOR)
        self.max_frame = tk.Frame(self.frame, bg=BG_COLOR)
        self.min_frame.grid(row=0, column=1)
        self.middle_frame.grid(row=0, column=2)
        self.max_frame.grid(row=0, column=3, padx=3)

        tk.Label(self.min_frame, text="from", bg=BG_COLOR, fg=ACCENT_COLOR).grid(row=0)
        self.min_spin = tk.Spinbox(self.min_frame, from_=1, to=20, width=2, bg=ACCENT_COLOR, fg=FONT_CLEAR_COLOR,
                                   insertbackground=FONT_CLEAR_COLOR, relief='flat',
                                   command=self.update_max, textvariable=self.min)

        self.min_spin.grid(row=1)

        tk.Label(self.middle_frame, text="", bg=BG_COLOR, fg=ACCENT_COLOR).grid(row=0)
        tk.Label(self.min_frame, text="", bg=BG_COLOR).grid(row=2)
        tk.Label(self.middle_frame, text="", bg=BG_COLOR).grid(row=2)
        tk.Label(self.max_frame, text="", bg=BG_COLOR).grid(row=2)
        tk.Label(self.middle_frame, text="..", bg=BG_COLOR, fg=ACCENT_COLOR).grid(row=1)
        tk.Label(self.max_frame, text="to", bg=BG_COLOR, fg=ACCENT_COLOR).grid(row=0, sticky='w')
        self.max_spin = tk.Spinbox(self.max_frame, from_=1, to=20, width=2, bg=ACCENT_COLOR, fg=FONT_CLEAR_COLOR,
                                   insertbackground=FONT_CLEAR_COLOR, relief='flat',
                                   command=self.update_min, textvariable=self.max)
        self.max_spin.grid(row=1)

        self.min.trace('w', update_query)
        self.max.trace('w', update_query)

        self.min_frame.grid_remove()
        self.middle_frame.grid_remove()
        self.max_frame.grid_remove()


Line()
update_query()
root.mainloop()
