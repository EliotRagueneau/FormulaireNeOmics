from HoveringInfo import *

root = Tk()
x = Label(root, text="test")
x.pack()
HoverInfo(x,"description")
root.mainloop()