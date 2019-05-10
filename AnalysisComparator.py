import tulipplugins
from tulip import tlp


def subgraphGrid(multiple_graph, nbcolumn):
    """
    Align all the subgraph of a graph, in a grid.

    Args:
        multiple_graph (tlp.Graph): A parent graph
        nbcolumn (int): number of column in the grid
    """
    # get one subgraph's bounding box
    boundingBox = tlp.computeBoundingBox(multiple_graph.getNthSubGraph(1))
    number_of_visited_subgraph = 0
    size_X = 2.5 * abs(boundingBox[1][0] - boundingBox[0][0])
    # we multiply by 2.5 (2*radius + 0.5 to have a small padding)
    size_Y = 2.5 * abs(boundingBox[1][1] - boundingBox[0][1])
    # we multiply by 2.5 (2*radius + 0.5 to have a small padding)
    offset_X = number_of_visited_subgraph * size_X
    offset_Y = number_of_visited_subgraph * size_Y
    layout = multiple_graph.getLayoutProperty("viewLayout")
    for multiple_graph in multiple_graph.getSubGraphs():
        number_of_visited_subgraph += 1
        for node in multiple_graph.getNodes():
            layout[node] += layout[node] + tlp.Vec3f(offset_X, -offset_Y, 0)
        for edge in multiple_graph.getEdges():
            control_points = layout[edge]
            new_control_points = []
            for vector in control_points:
                new_control_points.append(tuple(map(sum, zip(vector, (offset_X, -offset_Y, 0)))))
            layout[edge] = new_control_points
        offset_X = number_of_visited_subgraph % nbcolumn * size_X
        offset_Y = (number_of_visited_subgraph // nbcolumn) * size_Y


class AnalysisComparator(tlp.Algorithm):
    def __init__(self, context):
        tlp.Algorithm.__init__(self, context)
        # you can add parameters to the plugin here through the following syntax
        # self.add<Type>Parameter("<paramName>", "<paramDoc>", "<paramDefaultValue>")
        # (see documentation of class tlp.WithParameter to see what types of parameters are supported)
        self.addDirectoryParameter("Directory path",
                                   defaultValue="/home/eliot/Documents/Travail/M1/Projets/FormulaireNeOmics/Ressources",
                                   isMandatory=True, help="The path to the file")

    def check(self):
        # This method is called before applying the algorithm on the input graph.
        # You can perform some precondition checks here.
        # See comments in the run method to know how to access to the input graph.

        # Must return a tuple (boolean, string). First member indicates if the algorithm can be applied
        # and the second one can be used to provide an error message
        return (True, "Ok")

    def run(self):
        # This method is the entry point of the algorithm when it is called
        # and must contain its implementation.

        # The graph on which the algorithm is applied can be accessed through
        # the "graph" class attribute (see documentation of class tlp.Graph).

        # The parameters provided by the user are stored in a dictionnary
        # that can be accessed through the "dataSet" class attribute.

        # The method must return a boolean indicating if the algorithm
        # has been successfully applied on the input graph.
        import tkinter as tk
        from tkinter.font import Font
        import py2neo as neo
        neo_graph = neo.Graph("bolt://localhost:7687", auth=("eliot", "1234"))
        root = tk.Tk()
        from ScrollingFrame import ScrollingFrame
        from tkentrycomplete import AutocompleteCombobox
        resources = self.dataSet["Directory path"]
        BG_COLOR = "#FFFFFF"
        ADD_ICON = tk.PhotoImage(file=resources + "/Add_button.png")
        REMOVE_ICON = tk.PhotoImage(file=resources + "/Remove_line.png")
        FONT = Font(family="Arial", size=10)
        root.title("Cypher Query Creator")
        root.configure(bg=BG_COLOR)
        test = tk.Frame(root)
        test.pack()
        work_frame = ScrollingFrame(test, root, height=400)
        work_frame.pack()
        line_frame = tk.Frame(work_frame.frame, relief='flat', bg=BG_COLOR)
        line_frame.pack()

        class Line:
            analysisLines = []
            analysis_options = [result["analysis"] for result in
                                neo_graph.run("MATCH (a:Analysis) RETURN a.name AS analysis")]
            tissues = [result["tissue"] for result in
                       neo_graph.run("MATCH (a:Tissue) RETURN a.name AS tissue")]

            def __init__(self):
                Line.analysisLines.append(self)

                self.frame = tk.Frame(line_frame, relief='flat', bg=BG_COLOR)
                self.frame.pack(anchor='w', padx=15)
                self.name = tk.Label(self.frame)
                self.name.grid(row=1, column=0)
                Line.update_line_numbers()

                self.tissue = tk.StringVar()
                self.tissue_box = AutocompleteCombobox(self.frame, textvariable=self.tissue, width=10,
                                                       cursor="hand2", font=FONT)
                self.tissue.trace('w', self.update_exp_options)
                tk.Label(self.frame, text="Tissue", font=FONT, bg=BG_COLOR).grid(row=0, column=1)
                self.tissue_box.grid(row=1, column=1)
                self.tissue_box.set_completion_list(Line.tissues)

                self.exp = tk.StringVar()
                self.exp_box = AutocompleteCombobox(self.frame, textvariable=self.exp, width=10,
                                                    cursor="hand2", font=FONT)
                self.exp.trace('w', self.update_analysis_options)
                tk.Label(self.frame, text="Experience", font=FONT, bg=BG_COLOR).grid(row=0, column=2)
                self.exp_box.grid(row=1, column=2)

                self.analysis = tk.StringVar()
                self.analysis_box = AutocompleteCombobox(self.frame, textvariable=self.analysis, width=10,
                                                         cursor="hand2", font=FONT)
                tk.Label(self.frame, text="Analysis", font=FONT, bg=BG_COLOR).grid(row=0, column=3)
                self.analysis_box.grid(row=1, column=3)

                self.remove_btn = tk.Button(self.frame, image=REMOVE_ICON, relief='flat', command=self.remove_line,
                                            bg=BG_COLOR,
                                            cursor="hand2", highlightthickness=0, bd=0, activebackground=BG_COLOR)
                self.remove_btn.grid(row=1, column=4)

            def update_exp_options(self, *args):
                self.exp_box.set_completion_list([result["exp"] for result in neo_graph.run(
                    "MATCH (:Tissue {{name:'{}'}})--(a:Experience) RETURN a.name AS exp".format(self.tissue.get()))])
                self.exp.set("")
                self.analysis.set("")

            def update_analysis_options(self, *args):
                self.analysis_box.set_completion_list([result["analysis"] for result in neo_graph.run(
                    "MATCH (:Experience{{name:'{}'}})--(:Tissue {{name:'{}'}})--(a:Analysis) RETURN a.name AS analysis".format(
                        self.exp.get(), self.tissue.get()))])
                self.analysis.set("")

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

            def __str__(self):
                return "{} on {} on {}".format(self.analysis.get(), self.exp.get(), self.tissue.get())

            @property
            def cypher(self):
                return "(:Experience{{name:'{}'}})--(:Tissue {{name:'{}'}})--(:Analysis {{name:'{}'}})".format(
                    self.exp.get(), self.tissue.get(), self.analysis.get())

            @staticmethod
            def new_line():
                Line()
                work_frame.on_frame_configure()
                work_frame.after(50, lambda: work_frame.scroll_to_end())

            @staticmethod
            def draw():

                small_multiple = self.graph.getSuperGraph().addSubGraph(name="Small Multiples")
                for analysis in Line.analysisLines:
                    subgraph = small_multiple.addSubGraph(name=str(analysis))
                    tlp.copyToGraph(subgraph, self.graph)
                    viewColor = subgraph.getLocalColorProperty('viewColor')
                    viewSize = subgraph.getSizeProperty("viewSize")
                    viewColor.setAllNodeValue(tlp.Color(163, 163, 163, 100))
                    viewColor.setAllEdgeValue(tlp.Color(163, 163, 163, 10))
                    name_to_node = {}
                    for node in subgraph.getNodes():
                        name_to_node[subgraph.getNodePropertiesValues(node)["name"]] = node
                    up_regulated = [result["name"] for result in neo_graph.run("MATCH " + analysis.cypher +
                                                                               "--(:Group {name:'up'})--(a) RETURN a.name as name")]
                    for name in up_regulated:
                        if name in name_to_node:
                            viewColor[name_to_node[name]] = tlp.Color(0, 255, 10, 255)
                            viewSize.setNodeValue(name_to_node[name], tlp.Size(20, 20, 20))
                    down_regulated = [result["name"] for result in neo_graph.run("MATCH " + analysis.cypher +
                                                                                 "--(:Group {name:'down'})--(a) RETURN a.name as name")]
                    for name in down_regulated:
                        if name in name_to_node:
                            viewColor[name_to_node[name]] = tlp.Color(255, 2, 2, 255)
                            viewSize.setNodeValue(name_to_node[name], tlp.Size(20, 20, 20))
                subgraphGrid(small_multiple, 2)
                root.destroy()

        add_button = tk.Button(work_frame.frame, image=ADD_ICON, relief='flat', command=Line.new_line, bg=BG_COLOR,
                               cursor="hand2", highlightthickness=0, bd=0, activebackground=BG_COLOR)
        add_button.pack(pady=5)
        send_btn = tk.Button(root, text="Draw", relief='flat', command=Line.draw, bg=BG_COLOR,
                             cursor="hand2", highlightthickness=0, bd=0, activebackground=BG_COLOR)
        send_btn.pack(side=tk.BOTTOM)
        Line.new_line()
        root.mainloop()

        return True


# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("AnalysisComparator", "Analysis comparator", "author", "26/07/2011", "info",
                                   "1.0", "Algorithm")
