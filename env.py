from Car import *
from GUI import GUI

import threading
import sys
import time

class Env():

    def __init__(self, numOpps, interval=50, action_size=(11, 11), action_range=(5, 1)):
        self.numOpps = numOpps
        self.agent = Agent(0, 0)
        self.opps = Opponents(numOpps)
        self.interval = interval
        self.action_size = action_size
        self.action_range = action_range # (accerelation, d_omega)
        aBin = action_range[0] * 2 / (action_size[0] - 1)
        domegaBin = action_range[1] * 2 / (action_size[1] - 1)
        self.action_bin = (aBin, domegaBin)
    
    def display(self, interval):
        gui = GUI(self.agent, self.opps, interval)
        gui.run()

    def reset(self):
        self.agent.reset()
        self.opps.reset()
        
        state = self.agent.getState()
        for o in self.agent.see(self.opps):
            state += list(o)
        state = np.array(state)
        return state

    def step(self, action):
        a = self.action_bin[0] * (int(action / self.action_size[1]) + 1 - (self.action_size[0] + 1) / 2)
        d_omega = self.action_bin[1] * (int(action % self.action_size[1]) + 1 - (self.action_size[1] + 1) / 2)
        
        self.agent.move(a, d_omega, self.interval / 1000)
        self.opps.move(self.interval / 1000)

        state = self.agent.getState()
        for o in self.agent.see(self.opps):
            state += list(o)
        obs = np.array(state)

        # just goal or not
        if (self.agent.goal()):
            reward = 1.0
        else:
            reward = 0.0

        done = self.agent.goal() or self.agent.crash(self.opps) or (not self.agent.inField()) 
        return (obs, reward, done)







def display(env, interval):
    env.display(interval)

def run(interval):
    time.sleep(2)
    for i in range(121):
        obs, reward, done = env.step(action=115)
        #print(obs, reward, done)
        if (done):
            print("done")
            break
        time.sleep(interval / 1000)


if __name__ == "__main__":

    args = sys.argv

    env = Env(6)
    env.reset()
    runThread = threading.Thread(target=run, args=(env.interval,))
    displayThread = threading.Thread(target=display, args=(env, env.interval))

    global flag
    flag = True
    try:
        runThread.start()
        displayThread.start()
        print("thread started")
        runThread.join()
        displayThread.join()
    except KeyboardInterrupt:
        flag = False