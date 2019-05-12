import tulipplugins
from tulip import tlp


class NeOmics(tlp.ImportModule):
    def __init__(self, context):
        tlp.ImportModule.__init__(self, context)
        self.addDirectoryParameter("Directory path",
                                   defaultValue="/net/stockage/PdP_BioInfo_2019/Gallardo_Ragueneau_Lambard/Ressources",
                                   isMandatory=True, help="The path to the file")
        self.addStringParameter("URI", help="URI", defaultValue="bolt://infini2:7687", isMandatory=True)
        self.addStringParameter("User name", help="Neo4j DB user name", defaultValue="neo4j", isMandatory=True)
        self.addStringParameter("Password", help="DB password", defaultValue="cremi", isMandatory=True)

    def importGraph(self):
        import tkinter as tk
        from tkinter.font import Font
        import py2neo as neo
        neo_graph = neo.Graph(self.dataSet["URI"], auth=(self.dataSet["User name"], self.dataSet["Password"]))
        root = tk.Tk()
        from ScrollingFrame import ScrollingFrame
        from tkentrycomplete import AutocompleteCombobox
        from string import ascii_lowercase
        import itertools

        # ---- Ressources Loading ----
        ressources = self.dataSet["Directory path"]

        bg_color = "#FFFFFF"
        accent_color = "#A2A2A2"
        font_clear_color = "white"
        font_dark_color = "#C4C4C4"
        add_icon = tk.PhotoImage(file=ressources + "/Add_button.png")
        remove_icon = tk.PhotoImage(file=ressources + "/Remove_line.png")
        font = Font(family="Arial", size=10)
        morceau = tk.PhotoImage(file=ressources + "/morceau.png")
        nodes_img = {"Tissue"    : tk.PhotoImage(file=ressources + "/Tissue.png"),
                     "Analysis"  : tk.PhotoImage(file=ressources + "/Analysis.png"),
                     "Experience": tk.PhotoImage(file=ressources + "/Exp.png"),
                     "TF"        : tk.PhotoImage(file=ressources + "/TF.png"),
                     "GOI"       : tk.PhotoImage(file=ressources + "/GOI.png"),
                     "Gene"      : tk.PhotoImage(file=ressources + "/Gene.png"),
                     "Protein"   : tk.PhotoImage(file=ressources + "/Protein.png"),
                     "Annotation": tk.PhotoImage(file=ressources + "/Annot.png"),
                     "Group"     : tk.PhotoImage(file=ressources + "/Group.png"),
                     "Unknown"   : tk.PhotoImage(file=ressources + "/Unknown_node.png")

                     }

        # ---- GUI configuration ----
        root.title("Cypher Query Creator")
        root.configure(bg=bg_color)

        query = tk.StringVar()
        query.set("MATCH")
        tk.Label(root, textvariable=query, width=40, anchor='e', bg=bg_color, font=font).pack()

        nodes = []

        def id_generator():
            """Generate id by alphabetical order"""
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

        # Draw line to separate the scrolling frame
        line_width = 250
        upper_line_canvas = tk.Canvas(root, borderwidth=0, bg=bg_color, highlightthickness=0, height=8,
                                      width=line_width)
        upper_line_canvas.pack()
        upper_line_canvas.create_line(0, 5, line_width, 5, fill=accent_color)

        surrounding_frame = tk.Frame(root)
        surrounding_frame.pack()
        work_frame = ScrollingFrame(surrounding_frame, root)
        work_frame.pack(expand=True)

        # Draw line to separate the scrolling frame
        lower_line_canvas = tk.Canvas(root, borderwidth=0, bg=bg_color, highlightthickness=0, height=8,
                                      width=line_width)
        lower_line_canvas.pack()
        lower_line_canvas.create_line(0, 5, line_width, 5, fill=accent_color)

        def import_from_query():
            """Use the query drawer plugin to draw the built query"""
            params = tlp.getDefaultPluginParameters("QueryDrawer")
            params['Query'] = query.get()
            params['URI'] = self.dataSet['URI']
            params["User name"] = self.dataSet["User name"]
            params["Password"] = self.dataSet["Password"]
            params["Directory path"] = self.dataSet["Directory path"]
            tlp.copyToGraph(self.graph, tlp.importGraph("QueryDrawer", params))
            root.destroy()

        # Add the button to finish plugin execution by importing the graph described by the query
        tk.Button(root, text="Draw", command=import_from_query).pack()

        class Node:
            # TODO Add remove option
            # TODO Deal with several branches

            def __init__(self):
                nodes.append(self)

                self.frame = tk.Frame(work_frame.frame, relief='flat', bg=bg_color)
                self.frame.pack(anchor='w', padx=15)

                self.node_button = tk.Button(self.frame, image=nodes_img['Unknown'], relief='flat', bg=bg_color,
                                             cursor="hand2",
                                             highlightthickness=0, bd=0, activebackground=bg_color,
                                             command=self.display_types,
                                             font=font)
                self.node_button.grid(row=0, column=0)
                self.node_type = ""
                self.returned = tk.IntVar()
                tk.Checkbutton(self.frame, variable=self.returned, text="name : ", bg=bg_color, highlightthickness=0,
                               bd=0, font=font, activebackground=bg_color).grid(row=0, column=1)
                self.returned.trace('w', update_global_query)

                self.name = tk.StringVar()
                self.name_options = []
                self.name_box = AutocompleteCombobox(self.frame, textvariable=self.name, width=20, cursor="hand2",
                                                     font=font)
                self.name.trace('w', update_global_query)
                self.name_box.grid(row=0, column=2)
                self.add_button = tk.Button(self.frame, image=add_icon, relief='flat', command=self.new_node,
                                            bg=bg_color,
                                            cursor="hand2", highlightthickness=0, bd=0, activebackground=bg_color)
                self.add_button.grid(row=2, column=0)
                self.link = None
                self.next = None
                self.choice_inner_frame = None
                self.choice_frame = tk.Frame(self.frame, {"width" : 0,
                                                          "height": 5,
                                                          "bg"    : bg_color})
                self.choice_frame.grid(row=1, columnspan=4)

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

            def display_types(self):
                """Display a node selection panel and set buttons to choose the type of node"""
                # TODO Fix the gap between MORCEAU and inner_frame
                # TODO Fix the gap between link and next line
                self.node_button.configure(command=lambda x=self.node_type: self.select_type(x))
                self.choice_frame.configure(bg=bg_color)
                for element in self.choice_frame.grid_slaves():
                    element.destroy()
                types_query = self.query + "(a) RETURN DISTINCT labels(a) as type"
                types = [result['type'][-1] for result in neo_graph.run(types_query)]
                types.append("Unknown")
                tk.Label(self.choice_frame, image=morceau, bg=bg_color, pady=0, anchor='s').grid(sticky='sw', padx=18)
                self.choice_inner_frame = tk.Frame(self.choice_frame, bg=font_dark_color)
                self.choice_inner_frame.grid()
                counter = -1
                for possible_type in types:
                    counter += 1
                    node_btn = tk.Button(self.choice_inner_frame, text=possible_type, relief='flat', bg=font_dark_color,
                                         cursor="hand2", font=font, fg=font_clear_color,
                                         highlightthickness=0, bd=0, activebackground=font_dark_color,
                                         command=lambda x=possible_type: self.select_type(x))
                    if possible_type in nodes_img:
                        node_btn.configure(image=nodes_img[possible_type])
                    node_btn.grid(row=(counter // 4), column=counter % 4, padx=5, pady=5)

            def select_type(self, node_type):
                """Select a type from the node selection panel previously built and destroy it"""
                self.node_button.configure(command=self.display_types)  # Reset Node button to display the type options

                # Eliminate node selection panel
                for element in self.choice_frame.grid_slaves():
                    element.destroy()
                self.choice_frame.configure({"width" : 0,
                                             "height": 5,
                                             "bg"    : bg_color})

                # Set node_type variable used after
                self.node_type = node_type if node_type != "Unknown" else ""

                # Change the display image accordingly to its type
                if node_type in nodes_img:
                    self.node_button.configure(image=nodes_img[node_type])
                else:
                    self.node_button.configure(image=nodes_img["Unknown"])

                # Update autocompletion list since the type has been set
                self.update_name_list()
                update_global_query()

            def update_name_list(self):
                """Set the autocompletion list accordingly to current node information"""
                name_query = self.query + '(a'
                if self.node_type:
                    name_query += ":{}".format(self.node_type)
                name_query += ') RETURN a.name'
                # completion list is a set to avoid repetition
                completion_set = {result['a.name'] for result in neo_graph.run(name_query) if
                                  result['a.name'] is not None}
                self.name_box.set_completion_list(completion_set)

            def new_node(self):
                """Add a new node to the list"""
                self.add_button.grid_forget()
                self.link = Relation(self)
                self.link.next.update_name_list()
                update_global_query()
                work_frame.on_frame_configure()
                work_frame.after(50, lambda: work_frame.scroll_to_end())

        class Relation:
            """A relation is a link between two ndoes. It can be either simple or composed.
            A simple relation is a simple link between two adjacents nodes.
            A composed relation have a determined number of relations to travel through to reach the next node"""
            simple_link_icon = tk.PhotoImage(file=ressources + "/Lien.png")
            composed_link_icon = tk.PhotoImage(file=ressources + "/Composed_Link.png")

            def __init__(self, previous: Node):
                self.simple = True
                self.frame = tk.Frame(work_frame.frame, bg=bg_color)
                self.frame.pack(anchor='w', padx=45)
                self.icon = tk.Button(self.frame, relief='flat', image=self.simple_link_icon, command=self.switch,
                                      bg=bg_color,
                                      cursor="hand2", highlightthickness=0, bd=0, activebackground=bg_color)
                self.icon.grid(row=0, column=0)

                self.returned = tk.IntVar()
                tk.Checkbutton(self.frame, variable=self.returned, bg=bg_color, highlightthickness=0,
                               bd=0, activebackground=bg_color).grid(row=0, column=1)
                self.returned.trace('w', update_global_query)

                self.type_frame = tk.Frame(self.frame, bg=bg_color)
                self.type_frame.grid(row=0, column=2)
                tk.Label(self.type_frame, text="type :", font=font, bg=bg_color, fg=accent_color).pack(side="left")
                self.type = tk.StringVar()
                self.type_options = []
                self.type_box = AutocompleteCombobox(self.type_frame, textvariable=self.type, width=20, cursor="hand2",
                                                     font=font)
                self.type.trace('w', update_global_query)
                self.type_box.pack(side="right")

                self.min = tk.IntVar()
                self.max = tk.IntVar()

                self.min_frame = tk.Frame(self.frame, bg=bg_color)
                self.middle_frame = tk.Frame(self.frame, bg=bg_color)
                self.max_frame = tk.Frame(self.frame, bg=bg_color)
                self.min_frame.grid(row=0, column=2)
                self.middle_frame.grid(row=0, column=3)
                self.max_frame.grid(row=0, column=4, padx=3)

                tk.Label(self.min_frame, text="from", bg=bg_color, fg=accent_color, font=font).grid(row=0)
                self.min_spin = tk.Spinbox(self.min_frame, from_=1, to=20, width=2, bg=accent_color,
                                           fg=font_clear_color,
                                           insertbackground=font_clear_color, relief='flat',
                                           command=self.update_max, textvariable=self.min, font=font)

                self.min_spin.grid(row=1)

                tk.Label(self.middle_frame, text="", bg=bg_color, fg=accent_color).grid(row=0)
                for frame in [self.min_frame, self.middle_frame, self.max_frame]:
                    tk.Label(frame, text="", bg=bg_color).grid(row=2)

                tk.Label(self.middle_frame, text="..", bg=bg_color, fg=accent_color, font=font).grid(row=1)
                tk.Label(self.max_frame, text="to", bg=bg_color, fg=accent_color, font=font).grid(row=0, sticky='w')
                self.max_spin = tk.Spinbox(self.max_frame, from_=1, to=20, width=2, bg=accent_color,
                                           fg=font_clear_color,
                                           insertbackground=font_clear_color, relief='flat',
                                           command=self.update_min, textvariable=self.max, font=font)
                self.max_spin.grid(row=1)

                self.min.trace('w', update_global_query)
                self.max.trace('w', update_global_query)

                self.min_frame.grid_remove()
                self.middle_frame.grid_remove()
                self.max_frame.grid_remove()

                self.previous = previous
                self.next = Node()
                self.update_type_list()

            def update_type_list(self):
                """Updates type autocompletion list """
                type_query = self.previous.query + self.previous.descriptor + '-[r]-{} RETURN DISTINCT type(r) as types'.format(
                    self.next.descriptor)
                completion_list = {result['types'] for result in neo_graph.run(type_query) if 'types' in result}
                self.type_box.set_completion_list(completion_list)

            def switch(self):
                """Switch between simple and composed relation"""
                if self.simple:
                    self.simple = False
                    self.icon.configure(image=self.composed_link_icon)
                    self.type_frame.grid_remove()
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
                """Update max spinner value if min value is greater"""
                if self.max.get() < self.min.get():
                    self.max.set(self.min.get())

            def update_min(self):
                """Update min spinner value if max value is lower"""
                if self.max.get() < self.min.get():
                    self.min.set(self.max.get())

        init = Node()
        init.update_name_list()
        update_global_query()
        work_frame.on_frame_configure()
        root.mainloop()
        return True


# The line below does the magic to register the plugin into the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPlugin("NeOmics", "Query Maker", "Eliot Ragueneau et Jean Clément Gallardo", "11/05/2019",
                            "Help to build a cypher query describing a neo4j graph that will be drawn on Tulip", "1.0")
