import numpy as np
import copy

class Car:
    X_MAX = 5
    Y_MAX = 15    
    
    def __init__(self, x, y, theta, v):
        self.x = x # m
        self.y = y # m
        self.theta = theta # rad (-pi<theta<=pi)
        self.v = v # m/s
        
    def setV(self, v):
        self.v = v
    
    def setTheta(self, theta):
        self.theta = withinPi(theta)
    
    def setPosition(self, position):
        self.x = position[0]
        self.y = position[1]
        
    def getPosition(self):
        return (self.x, self.y)
    
class Agent(Car):
    MAX_SPEED = 5.0 # m/s^2
    MAX_OMEGA = 1.0 # rad/s^2
    MAX_OPPS = 5 # maximum number the agent can recognize
    VIEW_ANGLE = np.pi / 3 #viewing angle of this agent

    def __init__(self, x, y, theta=np.pi/2, v=MAX_SPEED/2, omega=0.0):
        super().__init__(x, y, theta, v)
        self.omega = omega
        self.opps = []
        
    def move(self, a, alpha, t):
        omega_mean = np.clip(self.omega + alpha * t / 2, -self.MAX_OMEGA, self.MAX_OMEGA) # average of omega in this time span
        self.omega = np.clip(self.omega + alpha * t, -self.MAX_OMEGA, self.MAX_OMEGA)
        theta_mean = self.theta + omega_mean * t / 2
        self.setTheta(self.theta + omega_mean * t) # -pi<theta<=pi
        v_mean = np.clip(self.v + a * t / 2, 0, self.MAX_SPEED)
        self.v = np.clip(self.v + a * t, 0, self.MAX_SPEED)
        dx = np.cos(theta_mean) * v_mean
        dy = np.sin(theta_mean) * v_mean
        self.x += dx * t
        self.y += dy * t

    # Return the opponent's relative position to this agent 
    def relPosition(self, opponent):
        x = opponent.x - self.x
        y = opponent.y - self.y
        r = np.sqrt(x ** 2 + y ** 2)
        if (x == 0):
            if (y >= 0):
                theta = np.pi / 2
            else:
                theta = -np.pi / 2
        else:
            theta = np.arctan2(y, x)
        
        theta = withinPi(theta - self.theta)
        return (r, theta)

    # Judge if the opponent is within this agent's viewing range
    def inRange(self, opponent):
        psi = self.relPosition(opponent)[1]
        return (- self.VIEW_ANGLE <= psi) and (psi <= self.VIEW_ANGLE)
    
    # Return list of opponents the agent can see
    def see(self, Opps):
        self.opps = []
        Opps.notSeen()
        # filter if the agent can view
        tmp = list(filter(self.inRange, Opps.list))
        # sort the opponents near to far
        tmp = sorted(tmp, key=lambda o: self.relPosition(o)[0])
        
        shade = [] # list of tupple of angle range covered by nearby opponents
        for o in tmp:
            pos = self.relPosition(o)
            inShade = False
            for s in shade:
                if ((s[0] <= pos[1]) and (pos[1] <= s[1])):
                    inShade = True
            if (not inShade):
                o.seen = True
                self.opps.append(o)
            
            phi = o.SIZE / pos[0]
            shade.append((pos[1] - phi/2, pos[1] + phi/2))

        # limit nearby MAX_OPPS number of opponent
        self.opps = self.opps[0:self.MAX_OPPS]
        # sort the opponents left to right
        self.opps = sorted(self.opps, key=lambda o: self.relPosition(o)[1], reverse=True)
        return self.opps

    def inField(self):
        return (-self.X_MAX <= self.x) and (self.x <= self.X_MAX) and (0 <= self.y) and (self.y <= self.Y_MAX)

    

class Opponent(Car):
    MAX_SPEED = 1.5
    ACCELERATION = 1.5
    OMEGA = np.pi / 3
    SIZE = 0.5 # size (m)
    
    def __init__(self, x, y, theta, v):
        super().__init__(x, y, theta, v)
        self.seen = False # if it's seen by the agent
    
        
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

    # reset all the opponents to not being seen
    def notSeen(self):
        for o in self.list:
            o.seen = False


# Function changing theta from -pi to pi (-pi<theta<=pi)
def withinPi(theta):
    if (theta > np.pi):
        theta -= 2 * np.pi
    elif (theta <= -np.pi):
        theta += 2 * np.pi
    return theta