import numpy as np

class Car:
    X_MAX = 5
    Y_MAX = 15    
    
    def __init__(self, x, y, theta, v):
        self.x = x
        self.y = y
        self.theta = theta
        self.v = v
        
    def setV(self, v):
        self.v = v
    
    def setTheta(self, theta):
        self.theta = theta
    
    def setPosition(self, position):
        self.x = position[0]
        self.y = position[1]
        
    def getPosition(self):
        return (self.x, self.y)
    
class Agent(Car):
    def __init__(self, x, y, theta, v):
        super().__init__(x, y, theta, v)
        
    def move(self, v, omega, t):
        self.v = v
        dx = np.cos(self.theta + omega * t / 2) * self.v
        dy = np.sin(self.theta + omega * t / 2) * self.v
        self.x += dx * t
        self.y += dy * t
        self.theta += omega * t
        
class Opponent(Car):
    MAX_SPEED = 5
    ACCELERATION = 5
    OMEGA = np.pi * 2 / 3
    
    def __init__(self, x, y, theta, v):
        super().__init__(x, y, theta, v)
    
        
    def move(self, t):
        self.x -= np.cos(self.theta) * self.v * t
        self.y -= np.sin(self.theta) * self.v * t
        self.randomNextV(t)
        self.randomNextTheta(t)
            
    # Return random v for the next step
    def randomNextV(self, t):
        self.v += np.random.randn() * self.ACCELERATION * t
        if (self.v > self.MAX_SPEED):
            self.v = self.MAX_SPEED
        elif (self.v < 0):
            self.v = 0
            
    # Return random theta for the next step
    def randomNextTheta(self, t):
        self.theta += np.random.randn() * self.OMEGA * t
        if (self.theta > np.pi):
            self.theta = np.pi
        elif (self.theta < 0):
            self.theta = 0
            
class Opponents():
    def __init__(self, n):
        self.list = []
        self.length = n
        for i in range(n):
            x = (np.random.random() * 2 - 1) * Car.X_MAX
            y = (np.random.random() * 2 + 1) * Car.Y_MAX / 3
            theta = np.pi * np.random.rand()
            v = np.random.random() * Opponent.MAX_SPEED
            self.list.append(Opponent(x, y, theta, v))
            
    def getPositions(self):
        return [opp.getPosition() for opp in self.list]
    
    def get(self, index):
        return self.list[index]

    def move(self, t):
        for i in self.list:
            i.move(t)