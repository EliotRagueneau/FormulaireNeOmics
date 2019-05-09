import tkinter as tk
from tulip import tlp
import tulipplugins
import py2neo as neo
from tkinter.font import Font
from PIL import Image, ImageTk


class AnalysisComparator(tlp.Algorithm):
    def __init__(self, context):
        tlp.Algorithm.__init__(self, context)
        # you can add parameters to the plugin here through the following syntax
        # self.add<Type>Parameter("<paramName>", "<paramDoc>", "<paramDefaultValue>")
        # (see documentation of class tlp.WithParameter to see what types of parameters are supported)

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
        neo_graph = neo.Graph("bolt://localhost:11016", auth=("eliot", "1234"))
        root = tk.Tk()
        from ScrollingFrame import ScrollingFrame
        from tkentrycomplete import AutocompleteCombobox
        resources = "C:/Users/Eliot/PycharmProjects/FormulaireNeOmics/Ressources"
        BG_COLOR = "#FFFFFF"
        ADD_ICON = tk.PhotoImage(file=resources + "/Add_button.png")
        REMOVE_ICON = tk.PhotoImage(file=resources + "/Remove_line.png")
        FONT = Font(family="Arial", size=10)

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
                        self.exp.get(),self.tissue.get()))])
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
                return "(:Experience{{name:'{}'}})--(:Tissue {{name:'{}'}})--(:Analysis {{name:'{}'}})".format( self.exp.get(), self.tissue.get(),self.analysis.get())

            @staticmethod
            def new_line():
                Line()
                work_frame.on_frame_configure()
                work_frame.after(50, lambda: work_frame.scroll_to_end())

            @staticmethod
            def draw():
                graph = AnalysisComparator.graph
                small_multiple = graph.addSubGraph(selection=None, name="Small Multiples")
                for analysis in Line.analysisLines:
                    subgraph = small_multiple.addSubGraph(name=str(analysis))
                    tlp.copyToGraph(subgraph, graph)
                    up_regulated = [result["name"] for result in neo_graph.run("MATCH " + analysis.cypher +
                                                                               "--(:Group {name:'up'})--(a) RETURN a.name as name")]
                    raise Exception("MATCH " + analysis.cypher + "--(:Group {name:'up'})--(a) RETURN a.name as name")
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
