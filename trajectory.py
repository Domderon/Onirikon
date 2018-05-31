import random
import numpy

from level import Level

class Trajectory:
    # an array of directions, validate for maximum extend, and for non-crossing
    # direction: 0,1,2,3
    
    directions = [0, 1, 2, 3]
    offsets = [(-1,0), (1,0), (0,-1), (0,1)]
    
    def __init__(self):
        self.actions = []
        
    # initialize a trajactory in an empty level
    def initialize(self, level, min_length=1, max_length=10):
        self.level = level
        self.simple(level, min_length, max_length)
        return
    
    def get_traversed_cells(self):
        cells = { self.start }
        pos = self.start
        for action in self.actions:
            offset = self.offsets[action]
            pos = (pos[0] + offset[0], pos[1] + offset[1])
            cells.add(pos)
        return cells
        
    
    # generate a simple trajectory
    def simple(self, level, min_length, max_length):
        max_length = min(max_length, level.width-3)
        if min_length > max_length:
            raise ValueError("Max length < min length")
            return
        size = random.randint(min_length, max_length)

        y = random.randint(1,level.height-2)
        self.start = (1,y)
        for i in range(size):
            self.actions.append(1);

    # visualize trajectory in level  
    def draw(self):
        level = self.level.copy()
        
        pos = self.start
        level.set(pos, 2)
        for action in self.actions:
            offset = self.offsets[action]
            pos = (pos[0] + offset[0], pos[1] + offset[1])
            level.set(pos, 2)
        level.print()
        return
'''
l = Level(8, 6)
t = Trajectory()
t.initialize(l)
t.draw()
'''



