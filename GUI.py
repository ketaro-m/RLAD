import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import copy

class GUI(tk.Tk):
    WIDTH = 500
    HIGHT = 1000
    def __init__(self, env, interval):
        super(GUI, self).__init__()
        self.title("simulator")
        self.geometry("{}x{}+{}+{}".format(self.WIDTH, self.HIGHT, 100, 50))
        self.resizable(width=0, height=0)
        
        # self.env_copy = copy.deepcopy(env) # copy of env for set_qval
        self.env = env
        self.agent = env.agent
        self.opps = env.opps
        self.interval = interval
        self.q_values = []
        self.action = 0 # the action index number the agent takes
        self.qmap = [] # list to contain q_value map
        self.qmap_update = False # flag if update q_value mapping or not
        
        self.oppImage = Image.open("img/car.png")
        self.oppImageSeen = Image.open("img/car_seen.png")
        self.agentImage = Image.open("img/agent.png")
        self.set_widgets()
        # self.set_button()
        

    def run(self):
        self.after(250, self.update_widgets)
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
                tkimgs.append(ImageTk.PhotoImage(image=self.oppImage.rotate(angle, expand=True), master=self))
            else:  
                tkimgs.append(ImageTk.PhotoImage(image=self.oppImageSeen.rotate(angle, expand=True), master=self))
            #print("opponent "+str(i),", positoin "+str(position), ", angle "+str(angle))
            #print((int(position[0] * 60), int(position[1] * 60)))
            self.board.create_image(int(position[0] * self.WIDTH/10 + self.WIDTH/2), self.HIGHT - int(position[1] * self.WIDTH/10), image=tkimgs[i])
            
    def set_agent(self):
        global tkimg
        position = self.agent.getPosition()
        angle = self.agent.theta * 180 / np.pi
        tkimg = ImageTk.PhotoImage(image=self.agentImage.rotate(angle, expand=True), master=self)
        #print("agent", ", position "+str(position), ", angle "+str(angle))
        self.board.create_image(int(position[0] * self.WIDTH/10 + self.WIDTH/2), self.HIGHT - int(position[1] * self.WIDTH/10), image=tkimg)

    def set_qvals(self, action, q_values):
        self.q_values = q_values
        self.action = action
        self.qmap_update = True

    # mapping q_value where the agent moves
    def map_qvals(self):
        r = 2
        if self.qmap_update:
            q_values = self.q_values
            max_q = np.argmax(q_values)
            action = self.action
            self.qmap.clear()
            tmp = [(),()]
            if len(q_values):
                q_values = (q_values - min(q_values))/(max(q_values) - min(q_values)) # normalization
            for i in range(len(q_values)):
                agent_state = self.env.step_dummy(i)
                q_val = int(q_values[i] * 100)
                x = int(agent_state[0] * self.WIDTH/10 + self.WIDTH/2)
                y = int(self.HIGHT - agent_state[1] * self.WIDTH/10)
                if (i == max_q):
                    color = "yellow"
                    tmp[0] = (x, y, color)
                if (i == action):
                    color = "red"
                    tmp[1] = (x, y, color)
                else:
                    color = "gray" + str(q_val)
                    self.board.create_oval(x-r, y-r, x+r, y+r, fill=color)
                    self.qmap.append((x, y, color))
            for q in tmp:
                self.board.create_oval(q[0]-r, q[1]-r, q[0]+r, q[1]+r, fill=q[2])
                self.qmap.append(q)
            self.qmap_update = False
        else:
            for q in self.qmap:
                x = q[0]
                y = q[1]
                color = q[2]
                self.board.create_oval(x-r, y-r, x+r, y+r, fill=color)

            
    def set_button(self):
        self.button = tk.Button(self, text="next", bg="gray", command=self.update_widgets)
        self.button.place(x=0, y=0)
        #self.button.pack()
        
    def update_widgets(self):
        self.board.delete("all")
        self.set_goal()
        self.set_opponents()
        self.set_agent()
        self.map_qvals()
        self.after(self.interval, self.update_widgets)

    def set_interval(self, interval):
        self.interval = interval
