import tulipplugins
from tulip import tlp
from tulipgui import tlpgui


def copy_graph(dest_graph: tlp.Graph, src_graph: tlp.Graph):
    """Copy all element of a graph in another graph"""
    dest_graph.delEdges(dest_graph.getEdges())
    dest_graph.delNodes(dest_graph.getNodes())
    old_to_new = {}
    for node in src_graph.getNodes():
        old_to_new[node] = dest_graph.addNode(src_graph.getNodePropertiesValues(node))
    for edge in src_graph.getEdges():
        nodes = src_graph.ends(edge)
        dest_graph.addEdge(old_to_new[nodes[0]], old_to_new[nodes[1]], src_graph.getEdgePropertiesValues(edge))


def subgraph_grid(multiple_graph, nbcolumn):
    """
    Align all the subgraph of a graph, in a grid.
    
    Author:
        Pierre Jacquet
        Modfied by Eliot Ragueneau

    Args:
        multiple_graph (tlp.Graph): A parent graph
        nbcolumn (int): number of column in the grid
    """
    # get one subgraph's bounding box
    bounding_box = tlp.computeBoundingBox(multiple_graph.getNthSubGraph(1))
    size_x = 1.5 * abs(bounding_box[1][0] - bounding_box[0][0])
    size_y = 1.5 * abs(bounding_box[1][1] - bounding_box[0][1])
    # Multiplied by 1.5 to have an separation between graphs

    number_of_visited_subgraph = 0
    offset_x = 0
    offset_y = 0

    layout = multiple_graph.getLayoutProperty("viewLayout")
    for sub_graph in multiple_graph.getSubGraphs():
        number_of_visited_subgraph += 1
        for node in sub_graph.getNodes():
            layout[node] += tlp.Vec3f(offset_x, -offset_y, 0)  # Move the node by offsets values
        for edge in sub_graph.getEdges():
            control_points = layout[edge]
            new_control_points = []
            for vector in control_points:
                new_control_points.append(tuple(map(sum, zip(vector, (offset_x, -offset_y, 0)))))
            layout[edge] = new_control_points
        # Calculate the new offset value
        offset_x = number_of_visited_subgraph % nbcolumn * size_x
        offset_y = (number_of_visited_subgraph // nbcolumn) * size_y


class AnalysisComparator(tlp.Algorithm):
    def __init__(self, context):
        tlp.Algorithm.__init__(self, context)
        self.addDirectoryParameter("Ressources directory",
                                   defaultValue="/net/stockage/PdP_BioInfo_2019/Gallardo_Ragueneau_Lambard/Ressources",
                                   isMandatory=True, help="Path to the ressources directory containing GUI assets")
        self.addUnsignedIntegerParameter("# Columns", help="Number of columns to display", defaultValue="2",
                                         isMandatory=True)
        self.addStringParameter("URI", help="URI to the Neo4j database", defaultValue="bolt://infini2:7687",
                                isMandatory=True)
        self.addStringParameter("User name", help="Neo4j DB user name", defaultValue="neo4j", isMandatory=True)
        self.addStringParameter("Password", help="Neo4j DB password", defaultValue="cremi", isMandatory=True)

    def check(self):
        return True, "Ok"

    def run(self):
        import tkinter as tk
        from tkinter.font import Font
        import py2neo as neo
        root = tk.Tk()
        from ScrollingFrame import ScrollingFrame
        from tkentrycomplete import AutocompleteCombobox

        neo_graph = neo.Graph(self.dataSet["URI"], auth=(self.dataSet["User name"], self.dataSet["Password"]))

        # ---- Ressources Loading ----
        ressources = self.dataSet["Ressources directory"]
        bg_color = "#FFFFFF"
        add_icon = tk.PhotoImage(file=ressources + "/Add_button.png")
        remove_icon = tk.PhotoImage(file=ressources + "/Remove_line.png")
        font = Font(family="Arial", size=10)

        # ---- GUI configuration ----
        root.title("Analysis Comparator")
        root.configure(bg=bg_color)
        surrounding_frame = tk.Frame(root,  relief='flat', bg=bg_color)
        surrounding_frame.pack()
        work_frame = ScrollingFrame(surrounding_frame, root, height=400)
        work_frame.pack()
        method_frame = tk.Frame(work_frame.frame, relief='flat', bg=bg_color)
        method_frame.pack()

        class Method:
            methodLines = []
            analysis_options = [result["analysis"] for result in
                                neo_graph.run("MATCH (a:Analysis) RETURN a.name AS analysis")]
            tissues = [result["tissue"] for result in
                       neo_graph.run("MATCH (a:Tissue) RETURN a.name AS tissue")]

            def __init__(self):
                Method.methodLines.append(self)

                self.frame = tk.Frame(method_frame, relief='flat', bg=bg_color)
                self.frame.pack(anchor='w', padx=15)
                self.name = tk.Label(self.frame)
                self.name.grid(row=1, column=0)
                Method.update_methods_number()

                self.tissue = tk.StringVar()
                self.tissue_box = AutocompleteCombobox(self.frame, textvariable=self.tissue, width=10,
                                                       cursor="hand2", font=font)
                self.tissue.trace('w', self.update_exp_options)
                tk.Label(self.frame, text="Tissue", font=font, bg=bg_color).grid(row=0, column=1)
                self.tissue_box.grid(row=1, column=1)
                self.tissue_box.set_completion_list(Method.tissues)

                self.exp = tk.StringVar()
                self.exp_box = AutocompleteCombobox(self.frame, textvariable=self.exp, width=10,
                                                    cursor="hand2", font=font)
                self.exp.trace('w', self.update_analysis_options)
                tk.Label(self.frame, text="Experience", font=font, bg=bg_color).grid(row=0, column=2)
                self.exp_box.grid(row=1, column=2)

                self.analysis = tk.StringVar()
                self.analysis_box = AutocompleteCombobox(self.frame, textvariable=self.analysis, width=10,
                                                         cursor="hand2", font=font)
                tk.Label(self.frame, text="Analysis", font=font, bg=bg_color).grid(row=0, column=3)
                self.analysis_box.grid(row=1, column=3)

                self.remove_btn = tk.Button(self.frame, image=remove_icon, relief='flat', command=self.remove_method,
                                            bg=bg_color,
                                            cursor="hand2", highlightthickness=0, bd=0, activebackground=bg_color)
                self.remove_btn.grid(row=1, column=4)

            def update_exp_options(self, *args):
                """Update experience box options accordingly to the DataBase and the previous entries.

                   Called after setting tissue value.
                """
                self.exp_box.set_completion_list([result["exp"] for result in neo_graph.run(
                    "MATCH (:Tissue {{name:'{}'}})--(a:Experience) RETURN a.name AS exp".format(self.tissue.get()))])

                # ---- Reset next values ----
                self.exp.set("")
                self.analysis.set("")

            def update_analysis_options(self, *args):
                """Update analysis box options accordingly to the DataBase and the previous entries.

                   Called after setting experience value.
                """
                self.analysis_box.set_completion_list([result["analysis"] for result in neo_graph.run(
                    "MATCH (:Experience{{name:'{}'}})--(:Tissue {{name:'{}'}})--(a:Analysis) RETURN a.name AS analysis".format(
                        self.exp.get(), self.tissue.get()))])

                # ---- Reset next values ----
                self.analysis.set("")

            @staticmethod
            def update_methods_number():
                """Update number methods when list of method is altered"""
                n = 0
                for line in Method.methodLines:
                    n += 1
                    line.name.configure(text="Method {}: ".format(n))

            def remove_method(self):
                """Remove itself from the list of methods"""
                self.frame.destroy()
                Method.methodLines.remove(self)
                Method.update_methods_number()

            def is_complete(self):
                """Check if all the fields have been set"""
                return self.analysis.get() and self.exp.get() and self.tissue.get()

            def __str__(self):
                """Give a name for the method"""
                return "{} on {} on {}".format(self.analysis.get(), self.exp.get(), self.tissue.get())

            @property
            def cypher(self):
                """Return a cypher descriptor of itself"""
                return "(:Experience{{name:'{}'}})--(:Tissue {{name:'{}'}})--(:Analysis {{name:'{}'}})".format(
                    self.exp.get(), self.tissue.get(), self.analysis.get())

            @staticmethod
            def new_method():
                """Add a new method to the list"""
                Method()
                work_frame.on_frame_configure()
                work_frame.after(10, lambda: work_frame.scroll_to_end())

            @staticmethod
            def draw():
                """Draw all the methods of the list in subgraphs and color
                 its nodes accordingly to their expression status.
                 Assemble all the subgraphs in one parallel view
                 """
                # Check if all the methods are complete to draw them
                for method in Method.methodLines:
                    if not method.is_complete():
                        return False

                # Copy the original graph in a subgraph to keep it intact
                source = self.graph.addSubGraph("Source")
                copy_graph(source, self.graph)

                # Create a sibling graph of source which will get all the duplicated subgraphs
                parallel_multi_graph = self.graph.addSubGraph("Parallel Methods Analysis")

                for method in Method.methodLines:
                    # Create a duplicated subgraph
                    subgraph = parallel_multi_graph.addSubGraph(name=str(method))
                    copy_graph(subgraph, source)

                    name_to_node = {}  # Dictionary to associate a gene name to its node

                    # Set all nodes and edges of the subgraph to a neutral color
                    viewColor = subgraph.getColorProperty('viewColor')
                    viewSize = subgraph.getSizeProperty("viewSize")
                    viewColor.setAllEdgeValue(tlp.Color(128, 128, 128, 50))
                    for node in subgraph.getNodes():
                        viewColor[node] = tlp.Color(128, 128, 128, 50)
                        name_to_node[subgraph.getNodePropertiesValues(node)["name"]] = node

                    # Get up regulated gene names described by the current method by a cypher query
                    up_regulated = [result["name"] for result in neo_graph.run("MATCH " + method.cypher +
                                                                               "--(:Group {name:'up'})--(a) RETURN a.name as name")]
                    # Emphasize the up regulated nodes
                    for name in up_regulated:
                        if name in name_to_node:  # If the current graph have this gene
                            viewColor[name_to_node[name]] = tlp.Color(0, 204, 0, 255)  # Set the node green
                            viewSize.setNodeValue(name_to_node[name], tlp.Size(10, 10, 10))  # Make it bigger

                    # Get down regulated gene names described by the current method by a cypher query
                    down_regulated = [result["name"] for result in neo_graph.run("MATCH " + method.cypher +
                                                                                 "--(:Group {name:'down'})--(a) RETURN a.name as name")]
                    # Emphasize the up regulated nodes
                    for name in down_regulated:
                        if name in name_to_node:  # If the current graph have this gene
                            viewColor[name_to_node[name]] = tlp.Color(204, 0, 0, 255)  # Set the node red
                            viewSize.setNodeValue(name_to_node[name], tlp.Size(10, 10, 10))  # Make it bigger

                # Align the different sub graphs on a grid layout
                subgraph_grid(parallel_multi_graph, self.dataSet["# Columns"])

                # Set a view of the parallel multi graph and get its parameters
                node_link_view = tlpgui.createNodeLinkDiagramView(parallel_multi_graph)
                rendering_parameters = node_link_view.getRenderingParameters()
                background = node_link_view.state()
                scene = background['scene']

                rendering_parameters.setEdgeColorInterpolate(True)  # Set edge color interpolating from the node ones
                rendering_parameters.setLabelsDensity(-100)  # Don't show any label
                scene = scene.replace("<background>(255,255,255,255)</background>",  # Set the background to black
                                      "<background>(0,0,0,255)</background>")

                # Apply the changed parameters
                background['scene'] = scene
                node_link_view.setState(background)
                node_link_view.setRenderingParameters(rendering_parameters)

                # Finish the plugin execution
                root.destroy()

        # Method declaration is finished
        # Add button to add new methods
        add_button = tk.Button(work_frame.frame, image=add_icon, relief='flat', command=Method.new_method, bg=bg_color,
                               cursor="hand2", highlightthickness=0, bd=0, activebackground=bg_color)
        add_button.pack(pady=5)

        # Send button to finish program execution
        send_btn = tk.Button(root, text="Draw", command=Method.draw, cursor="hand2")
        send_btn.pack(side=tk.BOTTOM)

        # Add the first method
        Method.new_method()

        # Begin the GUI
        root.mainloop()

        return True


# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("AnalysisComparator", "Analysis comparator", "author", "26/07/2011", "info",
                                   "1.0", "Algorithm")
