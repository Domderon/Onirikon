from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN
from world import Action


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
        for event in data:
            if K_LEFT == event.key:
                action = Action.LEFT
            elif K_RIGHT == event.key:
                action = Action.RIGHT
            elif K_UP == event.key:
                action = Action.UP
            elif K_DOWN == event.key:
                action = Action.DOWN
        return action
