import sys
import threading
import numpy as np
import logging
import time
from Car import *
from GUI import GUI
import torch
from dqn_agent import DQNAgent
from env import Env

def run(env, dqn_agent, interval):
    time.sleep(2)
    state = env.reset()
    input()
    while (flag):
        action, q_values = dqn_agent.act(state)
        # comment out this if you don't wanna see the q_value plotting
        ##
        env.gui.set_qvals(action, q_values)
        a = env.action_bin[0] * (int(action / env.action_size[1]) + 1 - (env.action_size[0] + 1) / 2)
        d_omega = env.action_bin[1] * (int(action % env.action_size[1]) + 1 - (env.action_size[1] + 1) / 2)
        print(q_values)
        print("Action No.{}, Alpha={:.2f}, d_omega={:.2f}, QValue={}".format(action, a, d_omega, q_values[action]))
        ##

        ## comment out this if you don't wanna wait for Enter key to update states
        # input() # waiting for Enter input

        next_state,reward,done,goal_flag = env.step(action, display=True)
        state = next_state
        # env.opps.move(interval / 1000) #example
        # agent.move(np.random.randn() * 5, np.random.randn() / 2, interval / 1000) #example
        # #agent.move(0, 0, interval / 1000)
        # see = agent.see(opps)
        #print(len(see))
        if (env.agent.goal()):
            print("Goal!")
            break
        elif (not env.agent.inField()):
            print("out of field")
            break
        elif (env.agent.crash(env.opps)):
            print("crash")
            break
        # time.sleep(interval / 1000)
        
    print("finish")

def display(env, interval):
    env.display(interval)

    
def main():
    args = sys.argv
    # initialize the agent and opponents
    agent = Agent(0, 0, np.pi/2, 2.5)
    opps = Opponents(int(args[1]))
    # setting intervals
    actionInterval = 250 # interval to update the actions [ms]
    runInterval = 50
    displayInterval = 25
    # 
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    dqn_agent = DQNAgent(state_size = 5 + 4 * Agent.MAX_OPPS, action_size=11*11, seed = 0)
    dqn_agent.qnetwork_local.load_state_dict(torch.load("params/model_2021-04-06-06-16_3_50_250.pth", map_location=device))
    env = Env(int(args[1]), runInterval, actionInterval)
    env.reset()
    runThread = threading.Thread(target=run, args=(env, dqn_agent, runInterval))
    displayThread = threading.Thread(target=display, args=(env, displayInterval))
    # create and run threads
    # runThread = threading.Thread(target=run, args=(agent, opps, runInterval))
    # displayThread = threading.Thread(target=display, args=(agent, opps, displayInterval))
    
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
        
    time.sleep(2)
    print(threading.active_count())
    


if __name__ == "__main__":
    main()