from Car import *
from GUI import GUI

import threading
import sys
import time

class Env():

    def __init__(self, numOpps, runinterval=50, commandInterval=1000, action_size=(11, 11), action_range=(5, 1)):
        self.agent = Agent(0, 0)
        self.opps = Opponents(numOpps)
        self.runinterval = runinterval
        self.commandInterval = commandInterval
        self.action_size = action_size
        self.action_range = action_range # (accerelation, d_omega)
        aBin = action_range[0] * 2 / (action_size[0] - 1)
        domegaBin = action_range[1] * 2 / (action_size[1] - 1)
        self.action_bin = (aBin, domegaBin)
    
    def display(self, interval):
        self.gui = GUI(self, interval)
        self.gui.run()

    def reset(self):
        self.agent.reset()
        self.opps.reset()
        
        state = self.agent.getState()
        for o in self.agent.see(self.opps):
            state += list(o)
        state = np.array(state)
        return state

    # change the number of opps
    def change_opps(self, numOpps: int):
        self.opps.setNum(numOpps)

    def step(self, action, display=False):
        a = self.action_bin[0] * (int(action / self.action_size[1]) + 1 - (self.action_size[0] + 1) / 2)
        d_omega = self.action_bin[1] * (int(action % self.action_size[1]) + 1 - (self.action_size[1] + 1) / 2)
        
        for _ in range(int(self.commandInterval/self.runinterval)):
            self.agent.move(a, d_omega, self.runinterval / 1000)
            self.opps.move(self.runinterval / 1000)

            state = self.agent.getState()
            for o in self.agent.see(self.opps):
                state += list(o)
            obs = np.array(state)

            reward = self.reward_function()

            done = self.agent.goal() or self.agent.crash(self.opps) or (not self.agent.inField())
            flag = self.agent.goal() # flag just for debug
            if done:
                break
            if (display):
                time.sleep(self.runinterval / 1000)
        
        return (obs, reward, done, flag)

    # dummy step for visualizing agent's point after command
    def step_dummy(self, action):
        a = self.action_bin[0] * (int(action / self.action_size[1]) + 1 - (self.action_size[0] + 1) / 2)
        d_omega = self.action_bin[1] * (int(action % self.action_size[1]) + 1 - (self.action_size[1] + 1) / 2)
        return self.agent.move_dummy(a, d_omega, self.runinterval / 1000, int(self.commandInterval/self.runinterval))


    # define reward
    def reward_function(self):
        # just goal or not
        if (self.agent.goal()):
            reward = 1.0
        elif (self.agent.crash(self.opps) or (not self.agent.inField())):
            reward = -1.0
        else:
            reward = 0.0
            #reward = 1 / self.agent.dist2goal()
        
        return reward








def display(env, interval):
    env.display(interval)

def run(interval):
    time.sleep(2)
    for i in range(121):
        obs, reward, done, flag = env.step(action=115)
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