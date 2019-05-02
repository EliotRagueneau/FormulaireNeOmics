import tkinter as tk
from PIL import Image, ImageTk
root = tk.Tk()

BG_COLOR = "#FFFFFF"
ACCENT_COLOR = "#A2A2A2"
FONT_CLEAR_COLOR = "white"
FONT_DARK_COLOR = "#C4C4C4"

MORCEAU = tk.PhotoImage(file="Ressources/morceau.png")
NODES_IMG = {"Tissue": ImageTk.PhotoImage(Image.open("Ressources/Tissue.png")),
             "Analysis": ImageTk.PhotoImage(Image.open("Ressources/Analysis.png")),
             "Gene": ImageTk.PhotoImage(Image.open("Ressources/Gene.png")),
             "Protein": ImageTk.PhotoImage(Image.open("Ressources/Protein.png")),
             "Annotation": ImageTk.PhotoImage(Image.open("Ressources/Annot.png")),
             "Unknown": ImageTk.PhotoImage(Image.open("Ressources/Unknown_node.png"))
             }
ADD_ICON = tk.PhotoImage(file="Ressources/Add_button.png")
REMOVE_ICON = tk.PhotoImage(file="Ressources/Remove_line.png")
