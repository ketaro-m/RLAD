import numpy as np

class Car:
    X_MAX = 5
    Y_MAX = 15    
    
    def __init__(self, x, y, theta, v):
        self.x = x # m
        self.y = y # m
        self.theta = theta # rad 
        self.v = v # m/s
        
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
    MAX_SPEED = 5.0 # m/s^2
    MAX_OMEGA = 1.0 # rad/s^2

    def __init__(self, x, y, theta=np.pi/2, v=MAX_SPEED/2, omega=0.0):
        super().__init__(x, y, theta, v)
        self.omega = omega
        
    def move(self, a, alpha, t):
        omega_mean = np.clip(self.omega + alpha * t / 2, -self.MAX_OMEGA, self.MAX_OMEGA) # average of omega in this time span
        self.omega = np.clip(self.omega + alpha * t, -self.MAX_OMEGA, self.MAX_OMEGA)
        theta_mean = self.theta + omega_mean * t / 2
        self.theta = self.theta + omega_mean * t
        v_mean = np.clip(self.v + a * t / 2, 0, self.MAX_SPEED)
        self.v = np.clip(self.v + a * t, 0, self.MAX_SPEED)
        dx = np.cos(theta_mean) * v_mean
        dy = np.sin(theta_mean) * v_mean
        self.x += dx * t
        self.y += dy * t
        
class Opponent(Car):
    MAX_SPEED = 1.5
    ACCELERATION = 1.5
    OMEGA = np.pi / 3
    
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