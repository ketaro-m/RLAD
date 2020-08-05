import sys
import threading
import numpy as np
from Car import *
from GUI import GUI


def main():
    args = sys.argv
    ag = Agent(0, 0, np.pi/2, 2.5)
    o = Opponents(int(args[1]))
    print(threading.active_count())
    gui = GUI(ag, o, int(args[2]))
    gui.run()
    print(threading.active_count())


if __name__ == "__main__":
    main()