import tkinter as tk

root = tk.Tk()

BG_COLOR = "#FFFFFF"
ACCENT_COLOR = "#A2A2A2"
FONT_CLEAR_COLOR = "white"
FONT_DARK_COLOR = "#C4C4C4"

NODES_IMG = {"Tissue"    : tk.PhotoImage(file="Ressources/Tissue.png"),
             "Analysis"  : tk.PhotoImage(file="Ressources/Analysis.png"),
             "Gene"      : tk.PhotoImage(file="Ressources/Gene.png"),
             "Protein"   : tk.PhotoImage(file="Ressources/Protein.png"),
             "Annotation": tk.PhotoImage(file="Ressources/Annot.png")
             }
