from string import ascii_lowercase
from tkinter.font import *

from py2neo import Graph

from Colors import *
from ScrollingFrame import ScrollingFrame
from tkentrycomplete import AutocompleteCombobox

graph = Graph("localhost:7687", auth=("neo4j", "1234"))

font = Font(family="Roboto", size=10)

root.title("Cypher Query Creator")
root.configure(bg=BG_COLOR)

try:
    root.wm_title("Cypher Query Creator")
    root.wm_iconbitmap("icon.ico")
except:
    pass

query = tk.StringVar()
query.set("MATCH")
tk.Label(root, textvariable=query, width=40, anchor='e', bg=BG_COLOR, font=font).pack()

nodes = []


def id_generator():
    for size in itertools.count(1):
        for s in itertools.product(ascii_lowercase, repeat=size):
            yield "".join(s)


def update_global_query(*args):
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
        if node.node_type:
            matches += ":{}".format(node.node_type)
        if node.name.get() != "":
            matches += ' {{name: "{}" }}'.format(node.name.get())
        matches += ")"

        link = node.link
        if link:
            matches += "-["
            if link.simple:
                link_type = link.type.get()
                if link.returned.get() == 1:
                    link_id = next(ids)
                    matches += "{}".format(link_id)
                    returned += "{}, ".format(link_id)
                    return_sth = True
                if link_type:
                    matches += ":{}".format(link_type)
            else:
                matches += "*{}..{}".format(link.min.get(), link.max.get())
            matches += "]-"

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


class Line:
    # TODO Add remove option
    # TODO Add Send button (connexion with Tulip)
    # TODO Deal with several branches
    add_icon = tk.PhotoImage(file="Ressources/Add_button.png")
    entry_bg = tk.PhotoImage(file="Ressources/Entry_bg.png")
    remove_icon = tk.PhotoImage(file="Ressources/Remove_line.png")

    def __init__(self):
        nodes.append(self)

        self.frame = tk.Frame(work_frame.frame, relief='flat', bg=BG_COLOR)
        self.frame.pack(anchor='w', padx=15)

        self.node_button = tk.Button(self.frame, image=NODES_IMG['Unknown'], relief='flat', bg=BG_COLOR, cursor="hand2",
                                     highlightthickness=0, bd=0, activebackground=BG_COLOR, command=self.type_choice,
                                     font=font)
        self.node_button.grid(row=0, column=0)
        self.node_type = ""
        self.returned = tk.IntVar()
        tk.Checkbutton(self.frame, variable=self.returned, text="name : ", bg=BG_COLOR, highlightthickness=0,
                       bd=0, font=font, activebackground=BG_COLOR).grid(row=0, column=1)
        self.returned.trace('w', update_global_query)

        self.name = tk.StringVar()
        self.name_options = []
        self.name_box = AutocompleteCombobox(self.frame, textvariable=self.name, width=20, cursor="hand2", font=font)
        self.name.trace('w', update_global_query)
        self.name_box.grid(row=0, column=2)
        self.add_button = tk.Button(self.frame, image=self.add_icon, relief='flat', command=self.new_line, bg=BG_COLOR,
                                    cursor="hand2", highlightthickness=0, bd=0, activebackground=BG_COLOR)
        self.add_button.grid(row=2, column=0)
        self.link = None
        self.next = None
        self.choice_frame = tk.Frame(self.frame, {"width" : 0,
                                                  "height": 5,
                                                  "bg"    : BG_COLOR})
        self.choice_frame.grid(row=1, columnspan=4)
        self.update_name_list()

    @property
    def descriptor(self):
        cypher = "("
        if self.node_type:
            cypher += ":{}".format(self.node_type)
        if self.name.get() != "":
            cypher += ' {{name: "{}" }}'.format(self.name.get())
        return cypher + ")"

    @property
    def query(self):
        cypher = "MATCH "
        for node in nodes:
            if node is self:
                break
            cypher += node.descriptor

            link = node.link
            if link:
                link.update_type_list()
                cypher += "-["
                if link.simple:
                    link_type = link.type.get()
                    if link_type:
                        cypher += ":{}".format(link_type)
                else:
                    cypher += "*{}..{}".format(link.min.get(), link.max.get())
                cypher += "]-"
        return cypher

    def type_choice(self):
        # TODO Fix the gap between MORCEAU and inner_frame
        # TODO Fix the gap between link and next line
        self.node_button.configure(command=lambda x=self.node_type: self.select_node(x))
        self.choice_frame.configure(bg=BG_COLOR)
        for element in self.choice_frame.grid_slaves():
            element.destroy()
        types_query = self.query + "(a) RETURN DISTINCT labels(a) as type"
        types = [result['type'][0] for result in graph.run(types_query)]
        types.append("Unknown")
        tk.Label(self.choice_frame, image=MORCEAU, bg=BG_COLOR, pady=0, anchor='s').grid(sticky='sw', padx=18)
        self.choice_inner_frame = tk.Frame(self.choice_frame, bg=FONT_DARK_COLOR)
        self.choice_inner_frame.grid()
        counter = -1
        for possible_type in types:
            counter += 1
            node_btn = tk.Button(self.choice_inner_frame, text=possible_type, relief='flat', bg=FONT_DARK_COLOR,
                                 cursor="hand2", font=font, fg=FONT_CLEAR_COLOR,
                                 highlightthickness=0, bd=0, activebackground=FONT_DARK_COLOR,
                                 command=lambda x=possible_type: self.select_node(x))
            if possible_type in NODES_IMG:
                node_btn.configure(image=NODES_IMG[possible_type])
            node_btn.grid(row=(counter // 4), column=counter % 4, padx=5, pady=5)

    def select_node(self, node_type):
        self.node_button.configure(command=self.type_choice)
        for element in self.choice_frame.grid_slaves():
            element.destroy()
        self.choice_frame.configure({"width" : 0,
                                     "height": 5,
                                     "bg"    : BG_COLOR})
        self.node_type = node_type if node_type != "Unknown" else ""
        if node_type in NODES_IMG:
            self.node_button.configure(image=NODES_IMG[node_type])
        else:
            self.node_button.configure(image=NODES_IMG['Unknown'])
        self.update_name_list()
        update_global_query()

    def update_name_list(self):
        name_query = self.query + '(a'
        if self.node_type:
            name_query += ":{}".format(self.node_type)
        name_query += ') RETURN a.name'
        completion_list = {result['a.name'] for result in graph.run(name_query) if result['a.name'] is not None}
        self.name_box.set_completion_list(completion_list)

    def new_line(self):
        self.add_button.grid_forget()
        self.link = Link(self)
        update_global_query()
        work_frame.on_frame_configure()
        work_frame.after(50, lambda: work_frame.scroll_to_end())


class Link:
    simple_link_icon = tk.PhotoImage(file="Ressources/Lien.png")
    composed_link_icon = tk.PhotoImage(file="Ressources/Composed_Link.png")

    def __init__(self, previous: Line):
        self.simple = True
        self.frame = tk.Frame(work_frame.frame, bg=BG_COLOR)
        self.frame.pack(anchor='w', padx=45)
        self.icon = tk.Button(self.frame, relief='flat', image=self.simple_link_icon, command=self.switch, bg=BG_COLOR,
                              cursor="hand2", highlightthickness=0, bd=0, activebackground=BG_COLOR)
        self.icon.grid(row=0, column=0)

        self.returned = tk.IntVar()
        tk.Checkbutton(self.frame, variable=self.returned, bg=BG_COLOR, highlightthickness=0,
                       bd=0, activebackground=BG_COLOR).grid(row=0, column=1)
        self.returned.trace('w', update_global_query)

        self.type_frame = tk.Frame(self.frame, bg=BG_COLOR)
        self.type_frame.grid(row=0, column=2)
        tk.Label(self.type_frame, text="type :", font=font, bg=BG_COLOR, fg=ACCENT_COLOR).pack(side="left")
        self.type = tk.StringVar()
        self.type_options = []
        self.type_box = AutocompleteCombobox(self.type_frame, textvariable=self.type, width=20, cursor="hand2",
                                             font=font)
        self.type.trace('w', update_global_query)
        self.type_box.pack(side="right")

        self.min = tk.IntVar()
        self.max = tk.IntVar()

        self.min_frame = tk.Frame(self.frame, bg=BG_COLOR)
        self.middle_frame = tk.Frame(self.frame, bg=BG_COLOR)
        self.max_frame = tk.Frame(self.frame, bg=BG_COLOR)
        self.min_frame.grid(row=0, column=2)
        self.middle_frame.grid(row=0, column=3)
        self.max_frame.grid(row=0, column=4, padx=3)

        tk.Label(self.min_frame, text="from", bg=BG_COLOR, fg=ACCENT_COLOR, font=font).grid(row=0)
        self.min_spin = tk.Spinbox(self.min_frame, from_=1, to=20, width=2, bg=ACCENT_COLOR, fg=FONT_CLEAR_COLOR,
                                   insertbackground=FONT_CLEAR_COLOR, relief='flat',
                                   command=self.update_max, textvariable=self.min, font=font)

        self.min_spin.grid(row=1)

        tk.Label(self.middle_frame, text="", bg=BG_COLOR, fg=ACCENT_COLOR).grid(row=0)
        for frame in [self.min_frame, self.middle_frame, self.max_frame]:
            tk.Label(frame, text="", bg=BG_COLOR).grid(row=2)

        tk.Label(self.middle_frame, text="..", bg=BG_COLOR, fg=ACCENT_COLOR, font=font).grid(row=1)
        tk.Label(self.max_frame, text="to", bg=BG_COLOR, fg=ACCENT_COLOR, font=font).grid(row=0, sticky='w')
        self.max_spin = tk.Spinbox(self.max_frame, from_=1, to=20, width=2, bg=ACCENT_COLOR, fg=FONT_CLEAR_COLOR,
                                   insertbackground=FONT_CLEAR_COLOR, relief='flat',
                                   command=self.update_min, textvariable=self.max, font=font)
        self.max_spin.grid(row=1)

        self.min.trace('w', update_global_query)
        self.max.trace('w', update_global_query)

        self.min_frame.grid_remove()
        self.middle_frame.grid_remove()
        self.max_frame.grid_remove()

        self.previous = previous
        self.next = Line()
        self.update_type_list()

    def update_type_list(self):
        type_query = self.previous.query + self.previous.descriptor + '-[r]-{} RETURN DISTINCT type(r) as types'.format(
            self.next.descriptor)
        completion_list = {result['types'] for result in graph.run(type_query) if result['types'] is not None}
        print(completion_list)
        self.type_box.set_completion_list(completion_list)

    def switch(self):
        if self.simple:
            self.type_frame.grid_remove()
            self.simple = False
            self.icon.configure(image=self.composed_link_icon)
            self.min_frame.grid()
            self.middle_frame.grid()
            self.max_frame.grid()
        else:
            self.simple = True
            self.icon.configure(image=self.simple_link_icon)
            self.type_frame.grid()
            self.min_frame.grid_remove()
            self.middle_frame.grid_remove()
            self.max_frame.grid_remove()
        update_global_query()

    def update_max(self):
        if self.max.get() < self.min.get():
            self.max.set(self.min.get())

    def update_min(self):
        if self.max.get() < self.min.get():
            self.min.set(self.max.get())


Line()
update_global_query()
work_frame.on_frame_configure()
root.mainloop()
