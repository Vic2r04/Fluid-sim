import random
from functions import *

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = [random.randint(-20,20), random.randint(-20,20)]
        self.nextVel = [0,0]
        self.density = 0
        self.border = False
