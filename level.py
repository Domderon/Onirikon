# -*- coding: utf-8 -*-
"""
Created on Thu May 31 17:14:26 2018

@author: dominik.scherer
"""

import random
from enum import IntEnum

import numpy as np


class CellType(IntEnum):
    EMPTY = 0
    BLOCK = 1
    START = 2
    EXIT = 3
    TRAJECTORY = 4
    WINE = 5
    CHEESE = 6
    TORNADO = 7
    ICE = 8


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


class IceCell(Cell):
    def __init__(self):
        super().__init__('I')


class TornadoCell(Cell):
    def __init__(self):
        super().__init__('T')


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
        self.types = {
            CellType.EMPTY: EmptyCell,
            CellType.BLOCK: BlockCell,
            CellType.START: StartPositionCell,
            CellType.EXIT: ExitCell,
            CellType.TRAJECTORY: TrajectoryCell,
            CellType.WINE: WineCell,
            CellType.CHEESE: CheeseCell,
            CellType.TORNADO: TornadoCell,
            CellType.ICE: IceCell
        }
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
                self.set(cell, CellType.EMPTY)

    def set_start(self, pos):
        self.start = pos
        self.set(pos, CellType.START)

    def set_exit(self, pos):
        self.exit = pos
        self.set(pos, CellType.EXIT)
        
    def generate_from_trajectory(self, trajectory, density=0.1):
        self.set_start(trajectory.get_start())
        self.set_exit(trajectory.get_end())
        self.generate_simple(trajectory, density)
        
    def generate_simple(self, trajectory, density):
        blocked_cells = trajectory.get_traversed_cells()
        for i in range(1, self.width-1):
            for j in range(1, self.height-1):
                pos = (i,j)
                if pos not in blocked_cells:
                    if random.random() < density:
                        self.set(pos, CellType.BLOCK)
        
    def random_state(self):
        r = random.random()
        if r < 0.1:
            return CellType.CHEESE
        elif r < 0.2:
            return CellType.WINE
        elif r < 0.5:
            return CellType.BLOCK
        else:
            return CellType.EMPTY

    def generate_valid(self, trajectory, density = 0.2):
        from world import World

        self.set_start(trajectory.get_start())
        self.set_exit(trajectory.get_end())
        world = World(self)
        
        num_changes = density * self.width * self.height
        
        while num_changes != 0:
            # select a random cell
            cell = (random.randint(1,self.width-2), random.randint(1,self.height-2))
            # select a new state for this cell
            old_state = self.get(cell)
            new_state = self.random_state()
            self.set(cell, new_state)
            # validate that the new level is traversable by the trajectory
            if world.validate_trajectory(trajectory):
                num_changes -= 1
            else:
                self.set(cell, CellType(old_state))

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
