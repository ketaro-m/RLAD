import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

class GUI(tk.Tk):
    WIDTH = 500
    HIGHT = 1000
    def __init__(self, agent, opponents, interval):
        super(GUI, self).__init__()
        self.title("simulator")
        self.geometry("{}x{}+{}+{}".format(self.WIDTH, self.HIGHT, 100, 50))
        self.resizable(width=0, height=0)
        
        self.agent = agent
        self.opps = opponents
        self.interval = interval
        
        self.oppImage = Image.open("img/car.png")
        self.oppImageSeen = Image.open("img/car_seen.png")
        self.agentImage = Image.open("img/agent.png")
        self.set_widgets()
        # self.set_button()
        

    def run(self):
        self.after(2000, self.update_widgets)
        self.mainloop()
        
    def set_widgets(self):
        ### road ###
        self.board = tk.Canvas(self, width=self.WIDTH, height=self.HIGHT, bg="white")
        self.board.place(x=0, y=0)
        self.set_goal()
        self.set_opponents()
        self.set_agent()
        #self.board.pack()

    def set_goal(self):
        self.board.create_rectangle(self.WIDTH/2+self.WIDTH/10*self.agent.GOAL[0], self.HIGHT-self.WIDTH*3/2-40, self.WIDTH/2+self.WIDTH/10*self.agent.GOAL[1], self.HIGHT-self.WIDTH*3/2, fill="red")
        self.board.create_text(self.WIDTH/2, self.HIGHT-self.WIDTH*3/2-20, text="GOAL", font=("Arial", 10, "bold"), fill="yellow")
        self.board.create_line(0, self.HIGHT-self.WIDTH*3/2, self.WIDTH, self.HIGHT-self.WIDTH*3/2, fill='red')
        
        
    def set_opponents(self):
        global tkimgs
        tkimgs = []
        for i in range(len(self.opps.list)):
            # this judgement is needed because len(self.opps.list) might change during this loop
            if (i >= len(self.opps.list)):
                break
            position = self.opps.get(i).getPosition()
            angle = self.opps.get(i).theta * 180 / np.pi
            if (not self.opps.get(i).seen):
                tkimgs.append(ImageTk.PhotoImage(image=self.oppImage.rotate(angle, expand=True, fillcolor="white"), master=self))
            else:  
                tkimgs.append(ImageTk.PhotoImage(image=self.oppImageSeen.rotate(angle, expand=True, fillcolor="white"), master=self))
            #print("opponent "+str(i),", positoin "+str(position), ", angle "+str(angle))
            #print((int(position[0] * 60), int(position[1] * 60)))
            self.board.create_image(int(position[0] * self.WIDTH/10 + self.WIDTH/2), self.HIGHT - int(position[1] * self.WIDTH/10), image=tkimgs[i])
            
    def set_agent(self):
        global tkimg
        position = self.agent.getPosition()
        angle = self.agent.theta * 180 / np.pi
        tkimg = ImageTk.PhotoImage(image=self.agentImage.rotate(angle, expand=True, fillcolor="white"), master=self)
        #print("agent", ", position "+str(position), ", angle "+str(angle))
        self.board.create_image(int(position[0] * self.WIDTH/10 + self.WIDTH/2), self.HIGHT - int(position[1] * self.WIDTH/10), image=tkimg)
            
            
    def set_button(self):
        self.button = tk.Button(self, text="next", bg="gray", command=self.update_widgets)
        self.button.place(x=0, y=0)
        #self.button.pack()
        
    def update_widgets(self):
        self.board.delete("all")
        self.set_goal()
        self.set_opponents()
        self.set_agent()
        self.after(self.interval, self.update_widgets)
