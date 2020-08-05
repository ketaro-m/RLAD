import sys
import threading
from Car import *
from GUI import GUI


def main():
    args = sys.argv
    o = Opponents(int(args[1]))
    print(threading.active_count())
    gui = GUI(o, int(args[2]))
    gui.run()
    print(threading.active_count())


if __name__ == "__main__":
    main()