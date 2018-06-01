# -*- coding: utf-8 -*-
"""
Created on Thu May 31 17:14:26 2018

@author: dominik.scherer
"""

import random
from enum import Enum

import numpy as np


class CellType(Enum):
    EMPTY = 0
    BLOCK = 1
    START = 2
    EXIT = 3
    TRAJECTORY = 4
    WINE = 5
    CHEESE = 6


class Cell(object):
    def __init__(self, type, state=None):
        self.type = type
        self.state = state

    def get_state(self):
        return self.state

    def has_state(self):
        return self.get_state() is not None


class EmptyCell(Cell):
    def __init__(self):
        super().__init__(' ')


class BlockCell(Cell):
    def __init__(self):
        super().__init__('#')


class StartPositionCell(Cell):
    def __init__(self):
        super().__init__('S')


class ExitCell(Cell):
    def __init__(self):
        super().__init__('E')


# helper cell type for trajectory visualization
class TrajectoryCell(Cell):
    def __init__(self):
        super().__init__('*')


# Items.

class PickableItemCell(Cell):
    """
    Any object you can pick up.
    """

    def __init__(self, type):
        # Here the `state` indicates whether the item is still present.
        super().__init__(type=type, state=True)


class CheeseCell(PickableItemCell):
    def __init__(self):
        super().__init__('C')


class WineCell(PickableItemCell):
    def __init__(self):
        super().__init__('W')


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
        self.cells[:, 0] = CellType.BLOCK.value
        self.cells[:, self.width-1] = CellType.BLOCK.value
        self.cells[0, :] = CellType.BLOCK.value
        self.cells[self.height-1, :] = CellType.BLOCK.value

    def reset_trajectory(self, trajectory):
        cells = trajectory.get_traversed_cells()
        for cell in cells:
            if type(self.get_cell(*cell)) is BlockCell:
                self.set(cell, 0)

    def set_start(self, pos):
        self.start = pos
        self.set(pos, CellType.START)

    def set_exit(self, pos):
        self.exit = pos
        self.set(pos, CellType.EXIT)
        
    def generate_from_trajectory(self, trajectory, density=0.1):
        self.set_start(trajectory.get_start())
        self.set_exit(trajectory.get_end())

        blocked_cells = trajectory.get_traversed_cells()
        for i in range(1, self.width-1):
            for j in range(1, self.height-1):
                pos = (i,j)
                if pos not in blocked_cells:
                    if random.random() < density:
                        self.set(pos, CellType.BLOCK)

    def generate_from_matrix(self, matrix, trajectory = None):
        self.set_start(self.start)
        self.set_exit(self.exit)
        self.cells = matrix
        self.reset_border()
        if trajectory is not None:
            self.reset_trajectory(trajectory)

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

    def set(self, pos, cell_type):
        x, y = pos
        self.cells[y, x] = cell_type.value

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
