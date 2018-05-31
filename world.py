import copy

from enum import Enum
from level import BlockCell, EmptyCell, ExitCell, StartPositionCell


class Action(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


class World(object):

    def __init__(self, level):
        self.level = level
        self.init_state = None
        self.player_position_idx = None
        self.blocked = set()
        self.init()

    def get_player_position(self, state):
        return state[self.player_position_idx]

    def init(self):
        # Initialization: analyze the level to build the initial state.
        # First get the state of stateful cells.
        self.init_state = [cell.get_state() for _, cell in self.level.enumerate_cells() if cell.has_state()]
        # Add player position.
        for pos, cell in self.level.enumerate_cells():
            if isinstance(cell, StartPositionCell):
                self.init_state.append(pos)
                self.player_position_idx = len(self.init_state) - 1
            elif isinstance(cell, BlockCell):
                self.blocked.add(pos)
            elif isinstance(cell, (EmptyCell, ExitCell)):
                # Ignore.
                pass
            else:
                raise NotImplementedError(type(cell))
        assert self.player_position_idx is not None
        self.init_state = tuple(self.init_state)

    def perform(self, state, action):
        """
        Perform `action` in the given `state`.

        :return: The new state if the action was successful, or `None` otherwise.
        """
        x, y = self.get_player_position(state)
        if action == Action.DOWN:
            y += 1
        elif action == Action.UP:
            y -= 1
        elif action == Action.LEFT:
            x -= 1
        elif action == Action.RIGHT:
            x += 1
        else:
            raise NotImplementedError(action)
        if x < 0 or x >= self.level.width or y < 0 or y >= self.level.height or (x, y) in self.blocked:
            # Can't move!
            return None
        new_state = list(state)
        new_state[self.player_position_idx] = x, y
        return tuple(new_state)
