import sys
import threading
import numpy as np
import logging
import time
from Car import *
from GUI import GUI

def run(agent, opps, interval):
    time.sleep(2)
    while(flag):
        opps.move(interval / 1000) #example
        agent.move(agent.v, 0, interval / 1000) #example
        time.sleep(interval / 1000)
    print("finish")

def display(agent, opps, interval):
    gui = GUI(agent, opps, interval)
    gui.run()

    
def main():
    args = sys.argv
    # initialize the agent and opponents
    agent = Agent(0, 0, np.pi/2, 2.5)
    opps = Opponents(int(args[1]))
    # extract intervals
    runInterval = int(args[2])
    displayInterval = int(args[3])
    # create and run threads
    runThread = threading.Thread(target=run, args=(agent, opps, runInterval))
    displayThread = threading.Thread(target=display, args=(agent, opps, displayInterval))
    
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