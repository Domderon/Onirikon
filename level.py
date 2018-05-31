# -*- coding: utf-8 -*-
"""
Created on Thu May 31 17:14:26 2018

@author: dominik.scherer
"""

import numpy as np

class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = np.zeros((height, width), dtype=int)
        self.cells[:,0] = 1
        self.cells[:,width-1] = 1
        self.cells[0,:] = 1
        self.cells[height-1,:] = 1
        
    def copy(self):
        level = Level(self.width, self.height)
        level.cells = self.cells.copy()
        return level
        
    def size(self):
        return self.width, self.height
        
    def print(self):
        types = [' ', '#', '*']
        
        for i in range(self.height):
            for j in range(self.width):
                print(types[self.cells[i,j]], end = '')
            print("")
