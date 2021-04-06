import numpy as np
import copy

class Car:
    X_MAX = 5
    Y_MAX = 15
    SIZE = 0.5 # size [m]
    
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
    
    def inField(self):
        return (-self.X_MAX <= self.x) and (self.x <= self.X_MAX) and (0 <= self.y) and (self.y <= self.Y_MAX)
    
class Agent(Car):
    MAX_SPEED = 5.0 # m/s^2
    MIN_SPEED = 0.25 # m/s^2
    MAX_OMEGA = 1.0 # rad/s^2
    THETA_RANGE = (np.pi/6, np.pi*5/6)
    # THETA_RANGE = (0, np.pi)
    MAX_OPPS = 5 # maximum number the agent can recognize
    VIEW_ANGLE = np.pi / 3 #viewing angle of this agent
    GOAL = (-3.0, 3.0) # x-axis of the goal

    def __init__(self, x, y, theta=np.pi/2, v=MAX_SPEED/2, omega=0.0):
        super().__init__(x, y, theta, v)
        self.omega = omega
        self.opps = []

    def reset(self):
        self.setPosition((0, 0))
        self.setTheta(np.pi / 2)
        self.setV(self.MAX_SPEED/2)
        self.setOmega(0.0)

    def setOmega(self, omega):
        self.omega = omega

    def getState(self):
        return [self.x, self.y, self.theta, self.v, self.omega]

    # change theta range
    def setThetaRange(self, theta_range: tuple):
        self.THETA_RANGE = theta_range
        
    def move(self, a, alpha, t):
        omega_mean = np.clip(self.omega + alpha * t / 2, -self.MAX_OMEGA, self.MAX_OMEGA) # average of omega in this time span
        self.omega = np.clip(self.omega + alpha * t, -self.MAX_OMEGA, self.MAX_OMEGA)
        theta_mean = self.theta + omega_mean * t / 2
        self.setTheta(np.clip(self.theta + omega_mean * t, self.THETA_RANGE[0], self.THETA_RANGE[1])) # not allowing the agent to face backward
        v_mean = np.clip(self.v + a * t / 2, self.MIN_SPEED, self.MAX_SPEED)
        self.v = np.clip(self.v + a * t, self.MIN_SPEED, self.MAX_SPEED)
        dx = np.cos(theta_mean) * v_mean
        dy = np.sin(theta_mean) * v_mean
        self.x += dx * t
        self.y += dy * t

    # agent itself doesn't move but return (x, y, theta, v, omega) after n-steps
    def move_dummy(self, a, alpha, t, steps=1):
        x = self.x
        y = self.y
        theta = self.theta
        v = self.v
        omega = self.omega
        for _ in range(steps):
            omega_mean = np.clip(omega + alpha * t / 2, -self.MAX_OMEGA, self.MAX_OMEGA) # average of omega in this time span
            omega = np.clip(omega + alpha * t, -self.MAX_OMEGA, self.MAX_OMEGA)
            theta_mean = theta + omega_mean * t / 2
            theta = withinPi(np.clip(theta + omega_mean * t, self.THETA_RANGE[0], self.THETA_RANGE[1])) # not allowing the agent to face backward
            v_mean = np.clip(v + a * t / 2, self.MIN_SPEED, self.MAX_SPEED)
            v = np.clip(v + a * t, self.MIN_SPEED, self.MAX_SPEED)
            dx = np.cos(theta_mean) * v_mean
            dy = np.sin(theta_mean) * v_mean
            x = x + dx * t
            y = y + dy * t
        return (x, y, theta, v, omega)

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
        return [r, theta]

    # Return the opponent's relative velocity (dir, speed) to this agent
    def relVelocity(self, opponent):
        phi = opponent.theta - self.theta
        phi = withinPi(phi)
        speed = np.sqrt((opponent.v * np.cos(phi) + self.v)**2 + (opponent.v * np.sin(phi))**2)
        return [phi, speed]


    # Judge if the opponent is within this agent's viewing range
    def inRange(self, opponent):
        psi = self.relPosition(opponent)[1]
        return (- self.VIEW_ANGLE <= psi) and (psi <= self.VIEW_ANGLE)
    
    # Update self.opps, the list of opponents that the agent can see,
    # and return the list of the opponents-relative-state list [[x, y, theta, v], ...]  
    def see(self, Opps):
        self.opps = []
        Opps.notSeen()
        # filter if the opp is in field
        tmp = [o for o in Opps.list if o.inField]
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
        return [self.relPosition(o) + self.relVelocity(o) for o in self.opps]


    # true iff this agent crash with the opponents
    def crash(self, Opps):
        safty_distance = 0.2 # need to be set

        for o in Opps.list:
            x = o.x - self.x
            y = o.y - self.y
            r = np.sqrt(x ** 2 + y ** 2)
            if (r < self.SIZE/2 + Opponent.SIZE/2 + safty_distance):
                return True
        return False

    # true iff this agent reach the goal
    def goal(self):
        return (self.GOAL[0] < self.x and self.x < self.GOAL[1]) and (self.y >= self.Y_MAX-0.1)

    def dist2goal(self):
        return np.sqrt(self.x ** 2 + (self.y - self.Y_MAX) ** 2)

    

class Opponent(Car):
    Y_MAX = 20
    MAX_SPEED = 1.5
    THETA_RANGE = (np.pi/3, np.pi*2/3)
    ACCELERATION = 1.5
    OMEGA = np.pi / 3
    SIZE = 0.5 # size (m)
    
    def __init__(self, x, y, theta, v):
        super().__init__(x, y, theta, v)
        self.seen = False # if it's seen by the agent
    
    # reset its position
    def reset(self):
        x = (np.random.random() * 2 - 1) * self.X_MAX
        y = np.random.uniform(1/3, 1) * self.Y_MAX
        theta = np.clip(np.pi * np.random.rand(), self.THETA_RANGE[0], self.THETA_RANGE[1])
        v = np.random.random() * self.MAX_SPEED
        self.setPosition((x, y))
        self.setTheta(theta)
        self.setV(v)
        
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
        if (self.theta > self.THETA_RANGE[1]):
            self.theta = self.THETA_RANGE[1]
        elif (self.theta < self.THETA_RANGE[0]):
            self.theta = self.THETA_RANGE[0]
            
class Opponents():
    def __init__(self, n):
        self.list = []
        self.num = n
        for _ in range(n):
            opp = Opponent(0, 0, 0, 0)
            opp.reset()
            self.list.append(opp)

    def reset(self):
        if (len(self.list) < self.num):
            for i in range(self.num-len(self.list)):
                self.list.append(Opponent(0, 0, 0, 0))
        for opp in self.list:
            opp.reset()
            
    def getPositions(self):
        return [opp.getPosition() for opp in self.list]
    
    def get(self, index):
        return self.list[index]

    def move(self, t):
        for i in self.list:
            i.move(t)
            if not i.inField():
                # restart from randomized but y=Y_MAX point
                i.reset()
                i.setPosition((i.x, i.Y_MAX))

    # reset all the opponents to not being seen
    def notSeen(self):
        for o in self.list:
            o.seen = False

    # add opponents
    def add(self, num: int):
        self.num += num
        for _ in range(num):
            opp = Opponent(0, 0, 0, 0)
            opp.reset()
            self.list.append(opp)

    # delete opponents
    def delete(self, num: int):
        num = min(num, self.num) # not to make self.num negative
        self.num -= num
        for _ in range(num):
            del self.list[-1]

    # change opponents' num
    def setNum(self, num: int):
        diff = num - self.num
        if diff == 0:
            return
        elif diff > 0:
            self.add(diff)
        else:
            self.delete(-diff)
        


# Function changing theta from -pi to pi (-pi<theta<=pi)
def withinPi(theta):
    if (theta > np.pi):
        theta -= 2 * np.pi
    elif (theta <= -np.pi):
        theta += 2 * np.pi
    return theta