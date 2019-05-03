from tkinter.font import *
from ScrollingFrame import ScrollingFrame
from tkentrycomplete import AutocompleteCombobox
from tulip import tlp
import tulipplugins
from Colors import *
import py2neo


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
        neo_graph = py2neo.Graph("bolt://3.90.85.77:33014", auth=("neo4j", "dye-color-compressions"))

        font = Font(family="Arial", size=10)
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
            current_options = analysis_options.copy()

            def __init__(self):
                Line.analysisLines.append(self)

                self.frame = tk.Frame(line_frame, relief='flat', bg=BG_COLOR)
                self.frame.pack(anchor='w', padx=15)
                self.name = tk.Label(self.frame)
                self.name.grid(row=0, column=0)
                Line.update_line_numbers()

                self.analysis = tk.StringVar()
                self.analysis_box = AutocompleteCombobox(self.frame, textvariable=self.analysis, width=20,
                                                         cursor="hand2",
                                                         font=font)
                self.analysis.trace('w', Line.update_options)
                self.analysis_box.grid(row=0, column=1)
                self.analysis_box.set_completion_list(Line.current_options)

                self.remove_btn = tk.Button(self.frame, text="Remove", relief='flat', command=self.remove_line,
                                            bg=BG_COLOR,
                                            cursor="hand2", highlightthickness=0, bd=0, activebackground=BG_COLOR)
                self.remove_btn.grid(row=0, column=2)

            @staticmethod
            def update_options(*args):
                Line.current_options = Line.analysis_options.copy()
                for line in Line.analysisLines:
                    analysis_name = line.analysis.get()
                    if analysis_name:
                        Line.current_options.remove(analysis_name)
                for line in Line.analysisLines:
                    line.analysis_box.set_completion_list(Line.current_options)

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
                Line.update_options()

            @staticmethod
            def new_line():
                Line()
                work_frame.on_frame_configure()
                work_frame.after(50, lambda: work_frame.scroll_to_end())

            @staticmethod
            def draw():
                for analysis in Line.analysisLines:
                    up_regulated = [result["name"] for result in neo_graph.run("MATCH ")]

        add_button = tk.Button(work_frame.frame, text="ADD", relief='flat', command=Line.new_line, bg=BG_COLOR,
                               cursor="hand2", highlightthickness=0, bd=0, activebackground=BG_COLOR)
        add_button.pack(pady=5)
        send_btn = tk.Button(test, text="Draw", relief='flat', command=Line.draw, bg=BG_COLOR,
                             cursor="hand2", highlightthickness=0, bd=0, activebackground=BG_COLOR)
        send_btn.pack()
        Line.new_line()
        root.mainloop()

        return True


# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("AnalysisComparator", "Analysis comparator", "author", "26/07/2011", "info",
                                   "1.0", "Python")
