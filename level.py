# -*- coding: utf-8 -*-
"""
Created on Thu May 31 17:14:26 2018

@author: dominik.scherer
"""

import numpy as np
import random

class Cell():
    def __init__(self):
        pass

    def get_state(self):
        return None

    def has_state(self):
        return self.get_state() is not None


class EmptyCell(Cell):
    def __init__(self):
        self.type = ' '
        super().__init__()


class BlockCell(Cell):
    def __init__(self):
        self.type = '#'
        super().__init__()


class StartPositionCell(Cell):
    def __init__(self):
        self.type = 'S'
        super().__init__()


class ExitCell(Cell):
    def __init__(self):
        self.type = 'E'
        super().__init__()

class TrajectoryCell(Cell):
    def __init__(self):
        self.type = '*'
        super().__init__()


class Level:
    def load_level(level_filename):
        # TODO
        return Level(10, 10)

    def __init__(self, width, height):
        self.types = [EmptyCell, BlockCell, StartPositionCell, ExitCell, TrajectoryCell]
        self.width = width
        self.height = height
        self.cells = np.zeros((height, width), dtype=int)
        self.reset_border()
        self.start = None
        self.exit = None
        
    def reset_border(self):
        self.cells[:, 0] = 1
        self.cells[:, self.width-1] = 1
        self.cells[0, :] = 1
        self.cells[self.height-1, :] = 1

    def set_start(self, pos):
        self.start = pos
        self.set(pos, 2)

    def set_exit(self, pos):
        self.exit = pos
        self.set(pos, 3)
        
    def generate_from_trajectory(self, trajectory, density=0.1):
        self.set_start(trajectory.get_start())
        self.set_exit(trajectory.get_end())

        blocked_cells = trajectory.get_traversed_cells()
        for i in range(1, self.width-1):
            for j in range(1, self.height-1):
                pos = (i,j)
                if pos not in blocked_cells:
                    if random.random() < density:
                        self.set(pos, 1)

    def generate_from_matrix(self, matrix):
        self.set_start(self.start)
        self.set_end(self.end)
        self.cells = matrix
        self.reset_border()

    def copy(self):
        level = Level(self.width, self.height)
        level.cells = self.cells.copy()
        return level

    def enumerate_cells(self):
        """
        Iterate over all cells in the level.
        """
        for x in range(self.width):
            for y in range(self.height):
                yield (x, y), self.get_cell(x, y)

    def size(self):
        return self.width, self.height

    def set(self, pos, value):
        x, y = pos
        self.cells[y, x] = value

    def get(self, pos):
        x, y = pos
        return self.cells[y, x]

    def get_cell(self, x, y):
        return self.types[self.cells[y, x]]()

    def get_exit(self):
        if self.exit is not None:
            return self.exit, self.get_cell(self.exit[0], self.exit[1])
        else:
            raise RuntimeError('no exit cell!')

    def get_start(self):
        if self.start is not None:
            return self.start, self.get_cell(self.start[0], self.start[1])
        else:
            raise RuntimeError('no start cell!')

    def print(self):
        for i in range(self.height):
            for j in range(self.width):
                print(self.types[self.cells[i, j]]().type, end='')
            print("")
