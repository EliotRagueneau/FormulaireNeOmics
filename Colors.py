from pathlib import Path
from tkinter.font import Font
import tkinter as tk

resources = Path("C:/Users/Eliot/PycharmProjects/FormulaireNeOmics/Ressources")

BG_COLOR = "#FFFFFF"
ACCENT_COLOR = "#A2A2A2"
FONT_CLEAR_COLOR = "white"
FONT_DARK_COLOR = "#C4C4C4"

MORCEAU = tk.PhotoImage(str(resources / "morceau.png"))
NODES_IMG = {"Tissue": tk.PhotoImage(str(resources / "Tissue.png")),
             "Analysis": tk.PhotoImage(str(resources / "Analysis.png")),
             "Gene": tk.PhotoImage(str(resources / "Gene.png")),
             "Protein": tk.PhotoImage(str(resources / "Protein.png")),
             "Annotation": tk.PhotoImage(str(resources / "Annot.png")),
             "Unknown": tk.PhotoImage(str(resources / "Unknown_node.png"))
             }
ADD_ICON = tk.PhotoImage(str(resources / "Add_button.png"))
REMOVE_ICON = tk.PhotoImage(str(resources / "Remove_line.png"))
FONT = Font(family="Arial", size=10)
