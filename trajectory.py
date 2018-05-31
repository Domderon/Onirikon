import random
import numpy

from level import Level
from world import Action

class Trajectory:
    # an array of directions, validate for maximum extend, and for non-crossing
    # direction: 0,1,2,3
    
    directions = [0, 1, 2, 3]
    offsets = [(-1,0), (1,0), (0,-1), (0,1)]
    
    def __init__(self, level, min_length=1, max_length=10):
        self.actions = []
        self.level = level
        self.simple(level, min_length, level.width)
        
    def get_traversed_cells(self):
        cells = { self.start }
        pos = self.start
        for action in self.actions:
            offset = self.offsets[action]
            pos = (pos[0] + offset[0], pos[1] + offset[1])
            cells.add(pos)
        return cells

    def get_start(self):
        return self.start
    
    def get_end(self):
        pos = self.start
        for action in self.actions:
            offset = self.offsets[action]
            pos = (pos[0] + offset[0], pos[1] + offset[1])
        return pos
        
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
        for action in self.actions[:-1]:
            offset = self.offsets[action]
            pos = (pos[0] + offset[0], pos[1] + offset[1])
            level.set(pos, 2)
        level.print()
        return
'''
l = Level(10, 10)
t = Trajectory(l)
l.generate_from_trajectory(t, 0.1)
#t.draw()
l.print()
'''



