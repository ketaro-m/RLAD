import sys
from Car import *
from GUI import GUI


def main():
    args = sys.argv
    o = Opponents(int(args[1]))
    print(o.getPositions())
    o.move(1)
    print(o.getPositions())
    gui = GUI(o)
    gui.run()


if __name__ == "__main__":
    main()