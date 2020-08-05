import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

class GUI(tk.Tk):
    def __init__(self, opponents, interval):
        global tkimg
        super(GUI, self).__init__()
        self.title("simulator")
        self.geometry("{}x{}+{}+{}".format(600, 900, 100, 50))
        self.resizable(width=0, height=0)
        
        self.opps = opponents
        self.interval = interval
        
        img = Image.open("img/car.png")
        self.oppImage = img
        self.set_widgets()
        self.set_button()
        

    def run(self):
        self.after(2000, self.update_widgets)
        self.mainloop()
        
    def set_widgets(self):
        ### road ###
        self.board = tk.Canvas(self, width=600, height=930, bg="white")
        self.set_opponents()
        self.board.place(x=0, y=30)
        #self.board.pack()
        
    def set_opponents(self):
        global tkimgs
        tkimgs = []
        for i in range(self.opps.length):
            position = self.opps.get(i).getPosition()
            angle = self.opps.get(i).theta * 180 / np.pi
            tkimgs.append(ImageTk.PhotoImage(image=self.oppImage.rotate(angle, expand=True, fillcolor="white"), master=self))
            #print(i,position)
            #print((int(position[0] * 60), int(position[1] * 60)))
            self.board.create_image(int(position[0] * 60 + 300), 900 - int(position[1] * 60), image=tkimgs[i])
            
            
    def set_button(self):
        self.button = tk.Button(self, text="next", bg="gray", command=self.update_widgets)
        self.button.place(x=0, y=0)
        #self.button.pack()
        
    def update_widgets(self):
        self.opps.move(self.interval / 1000)
        #self.set_widgets()
        self.board.delete("all")
        self.set_opponents()
        self.after(self.interval, self.update_widgets)