from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN
from world import World, Action
from search import WorldGraph, a_star_search


class Controller:
    def __init__(self):
        pass

    def get_action(self, data):
        pass


class KeyboardController(Controller):
    def __init__(self):
        super().__init__()

    def get_action(self, data):
        action = None
        if data is not None:
            event = data
            if K_LEFT == event.key:
                action = Action.LEFT
            elif K_RIGHT == event.key:
                action = Action.RIGHT
            elif K_UP == event.key:
                action = Action.UP
            elif K_DOWN == event.key:
                action = Action.DOWN
        return action


class AStarController(Controller):
    ACTION_TICK_INTERVAL = 1

    def _compute_astar(self, level):
        self.level = level
        self.world = World(level=self.level)
        exit_position, exit_cell = self.level.get_exit()
        came_from, cost_so_far, current, n_steps = a_star_search(
              graph=WorldGraph(self.world), start=self.world.init_state,
              exit_definition=exit_position,
              extract_definition=self.world.get_player_position)

        self.path = []
        while True:
            if current is None:
                break
            self.path.append(self.world.get_player_position(current))
            current = came_from[current]
        self.path.reverse()

    def __init__(self, level):
        self.tick = 0
        self._compute_astar(level)
        super().__init__()

    def _get_action(self, src, dst):
        x_delta = src[0] - dst[0]
        y_delta = src[1] - dst[1]
        if x_delta == 1:
            action = Action.LEFT
        elif x_delta == -1:
            action = Action.RIGHT
        elif y_delta == -1:
            action = Action.DOWN
        elif y_delta == 1:
            action = Action.UP
        else:
            raise 'WTF! a-star failed us - or my code is just shit'
        return action

    def get_action(self, data=None):
        self.tick += 1
        action = None
        if self.tick % self.ACTION_TICK_INTERVAL == 0:
            action = self._get_action(self.path[0], self.path[1])
            self.path.pop(0)
        return action
