#!/usr/bin/env pythonw

import os
import random
import sys
import queue
from multiprocessing import Process, Queue
from multiprocessing import Event as MultiEvent
import numpy as np

import pygame
from pygame.locals import QUIT, K_SPACE, KEYDOWN, USEREVENT
from pygame.event import Event

from GUI import Button
from GUI.locals import TOPLEFT, GREEN, GREY

from game_utils import GameUtils
from level import Level, EmptyCell, BlockCell, StartPositionCell, ExitCell, WineCell, CheeseCell, TornadoCell, IceCell
from search import WorldGraph, a_star_search
from controllers import KeyboardController, AStarController
from trajectory import RandomWalkTrajectory
from world import World
from optimize import optimize
from level import LEVEL_WIDTH, LEVEL_HEIGHT

# Initialize seed immediately to be safe (default = system clock, but you can use a fixed integer for debugging).
random.seed(None)


class CustomEvents:
    EVENT_MODE_CHANGED = USEREVENT
    EVENT_GO_NEXT_LEVEL = USEREVENT + 1


class EngineState:
    def __init__(self, mode, playing):
        self.mode = mode
        self.playing = playing
        self.optimizer_process = None
        self.output_queue = None
        self.stop_event = None
        self.go_next_level = False


class Menu:
    PANEL_WIDTH = 180
    PANEL_MARGIN_TOP = 80

    def __init__(self, display):
        self.display = display
        w, h = self.display.get_size()
        self.panel_pos = (w - self.PANEL_WIDTH, self.PANEL_MARGIN_TOP)
        self.optimizeButton = OptimizeButton(self.run_optimizer, self.panel_pos)
        self.keyboardModeButton = KeyboardModeButton(self.keyboard_mode, self.panel_pos)
        self.astarModeButton = AStarModeButton(self.astar_mode, self.panel_pos)
        self.nextLevelButton = NextLevelButton(self.next_level, self.panel_pos)
        self.gui_objects = [self.optimizeButton, self.keyboardModeButton, self.astarModeButton, self.nextLevelButton]
        self.should_run_optimizer = False

    def update(self, enginestate):
        if enginestate.mode == GameEngine.MODE_KEYBOARD:
            self.keyboardModeButton.activate()
            self.astarModeButton.deactivate()
        elif enginestate.mode == GameEngine.MODE_ASTAR:
            self.keyboardModeButton.deactivate()
            self.astarModeButton.activate()
        if self.should_run_optimizer:
            self.should_run_optimizer = False
            self._run_optimizer(enginestate)
        if enginestate.optimizer_process is not None and not enginestate.optimizer_process.is_alive():
            print('Optimizer process died')
            enginestate.optimizer_process = None
            enginestate.output_queue = None
            self.optimizeButton.set_disabled(False)
            enginestate.stop_event.set()

    def draw(self):
        for gui_object in self.gui_objects:
            gui_object.gui_element.render(self.display)

    def on_mouse_up(self):
        for gui_object in self.gui_objects:
            gui_object.on_mouse_up()

    def on_mouse_down(self):
        mouse = pygame.mouse.get_pos()
        for gui_object in self.gui_objects:
            if mouse in gui_object.gui_element:
                gui_object.on_mouse_down()

    def _run_optimizer(self, enginestate):
        enginestate.output_queue = Queue()
        enginestate.stop_event = MultiEvent()
        trajectory = RandomWalkTrajectory(level_width=LEVEL_WIDTH, level_height=LEVEL_HEIGHT)
        enginestate.optimizer_process = Process(target=optimize,
                                                kwargs=dict(output_queue=enginestate.output_queue,
                                                            stop_event=enginestate.stop_event,
                                                            trajectory=trajectory,
                                                            put_period=1))
        enginestate.optimizer_process.start()
        self.optimizeButton.set_disabled(True)

    def run_optimizer(self):
        self.should_run_optimizer = True

    def keyboard_mode(self):
        event = Event(CustomEvents.EVENT_MODE_CHANGED, message=GameEngine.MODE_KEYBOARD)
        pygame.event.post(event)

    def astar_mode(self):
        event = Event(CustomEvents.EVENT_MODE_CHANGED, message=GameEngine.MODE_ASTAR)
        pygame.event.post(event)

    def next_level(self):
        event = Event(CustomEvents.EVENT_GO_NEXT_LEVEL, message=None)
        pygame.event.post(event)


class MyButton:
    MODE_ACTIVATED_COLOR = (242, 142, 48)
    MODE_DEACTIVATED_COLOR = (219, 185, 151)
    MODE_DISABLED_COLOR = (181, 176, 171)

    def __init__(self, callback, panel_pos, name, label, x, y, w, h, activated_color=GREEN, deactivated_color=GREY):
        self.callback = callback
        self.panel_pos = panel_pos
        self.name = name
        self.activated_color = activated_color
        self.deactivated_color = deactivated_color
        self.gui_element = Button(self._do_action, (x + panel_pos[0], y + panel_pos[1]), (w, h), label,
                                  self.activated_color, anchor=TOPLEFT)
        self.down = False
        self.activated = True
        self.disabled = False

    def on_mouse_up(self):
        if self.down and not self.disabled:
            self.gui_element.unfocus()
            self.gui_element.release()
            self.down = False

    def on_mouse_down(self):
        if not self.down and not self.disabled:
            self.down = True
            self.gui_element.focus()
            self.gui_element.click()

    def activate(self):
        if not self.activated:
            self.gui_element.color = self.activated_color
            self.activated = True

    def deactivate(self):
        if self.activated:
            self.gui_element.color = self.deactivated_color
            self.activated = False

    def set_disabled(self, value):
        if value != self.disabled:
            self.disabled = value
            if self.disabled:
                self.gui_element.color = self.MODE_DISABLED_COLOR
            else:
                self.gui_element.color = self.activated_color

    def _do_action(self):
        self.callback()


class OptimizeButton(MyButton):
    def __init__(self, callback, panel_pos, x=0, y=0, w=100, h=40):
        super().__init__(callback, panel_pos, 'optimize', 'Optimize', x, y, w, h)


class KeyboardModeButton(MyButton):
    def __init__(self, callback, panel_pos, x=0, y=100, w=150, h=40,
                 activated_color=MyButton.MODE_ACTIVATED_COLOR, deactivated_color=MyButton.MODE_DEACTIVATED_COLOR):
        super().__init__(callback, panel_pos, 'keyboard', 'Keyboard Mode', x, y, w, h,
                         activated_color, deactivated_color)


class AStarModeButton(MyButton):
    def __init__(self, callback, panel_pos, x=0, y=150, w=150, h=40,
                 activated_color=MyButton.MODE_ACTIVATED_COLOR, deactivated_color=MyButton.MODE_DEACTIVATED_COLOR):
        super().__init__(callback, panel_pos, 'astar', 'A* Mode', x, y, w, h,
                         activated_color, deactivated_color)


class NextLevelButton(MyButton):
    def __init__(self, callback, panel_pos, x=0, y=300, w=150, h=40,
                 activated_color=GREEN):
        super().__init__(callback, panel_pos, 'next', 'NEXT LEVEL', x, y, w, h,
                         activated_color)


class GameEngine:
    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 768
    MARGIN_LEFT = 70
    MARGIN_TOP = 70
    CELL_SIZE = 32
    TICKS_PER_SECOND = 30
    SOUNDS = ['spawn', 'move', 'blocked', 'drink', 'eat', 'win']
    MODE_KEYBOARD = 'keyboard'
    MODE_ASTAR = 'astar'

    def _clear_screen(self):
        self.surface.fill((255, 255, 255))

    def _init_display(self, fullscreen):
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('Onirikon')
        surface = pygame.Surface(self.screen.get_size())
        self.surface = surface.convert_alpha()
        self.menu = Menu(self.screen)

    def _init_clock(self):
        self.clock = pygame.time.Clock()

    def _init_keyboard(self):
        pygame.key.set_repeat(1, 40)

    def _init_sound(self):
        self.sounds = {}
        for name in self.SOUNDS:
            try:
                self.sounds[name] = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'assets', 'sound',
                                                                    name + '.wav'))
            except FileNotFoundError:
                print('Warning: sound "%s" not found' % name)

    def _play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def _init_enginestate(self):
        self.enginestate = EngineState(self.MODE_KEYBOARD, True)

    def _set_mode(self, mode):
        self.enginestate.mode = mode
        if mode == self.MODE_KEYBOARD:
            self._initialize_controller(KeyboardController())
        elif mode == self.MODE_ASTAR:
            self._initialize_controller(AStarController(self.level))

    def _set_playing(self, playing):
        self.enginestate.playing = playing

    def __init__(self, fullscreen=False):
        self.level = None
        self.last_valid_level = None
        pygame.init()
        self._init_display(fullscreen)
        self._init_keyboard()
        self._init_clock()
        self._init_sound()
        self._init_enginestate()

    def _load_level(self, level_filename=None, level=None, trajectory=None):
        if level is not None:
            print(f'level_filename is not None')
            self.level = level
            self.trajectory = trajectory
            self.trajectory.draw()
        elif level_filename is None:
            print(f'level_filename is None')
            width, height = LEVEL_WIDTH, LEVEL_HEIGHT
            self.trajectory = RandomWalkTrajectory(width, height)
            self.level = Level(width, height)
            self.level.generate_from_trajectory(self.trajectory, 0.5)
        else:
            self.level = Level.load_level(level_filename)
        self.level_width, self.level_height = self.level.size()

    def _initialize_level(self):
        self.game_objects = []
        for x in range(self.level_width):
            for y in range(self.level_height):
                objs = []
                cell = self.level.get_cell(x, y)
                if type(cell) is EmptyCell:
                    objs.append(Empty(x, y))
                elif type(cell) is BlockCell:
                    objs.append(Block(x, y))
                elif type(cell) is StartPositionCell:
                    objs.append(Empty(x, y))
                    obj = Player(x, y)
                    self.player = obj
                elif type(cell) is ExitCell:
                    obj = Exit(x, y)
                    self.exit = obj
                    objs.append(obj)
                elif type(cell) is WineCell:
                    objs.append(Empty(x, y))
                    objs.append(Wine(x, y))
                elif type(cell) is CheeseCell:
                    objs.append(Empty(x, y))
                    objs.append(Cheese(x, y))
                elif type(cell) is TornadoCell:
                    objs.append(Empty(x, y))
                    objs.append(Tornado(x, y))
                elif type(cell) is IceCell:
                    objs.append(Empty(x, y))
                    objs.append(Ice(x, y))
                for obj in objs:
                    self.game_objects.append(obj)
        self.game_objects.append(self.player)

        self.world = World(self.level)
        self.state = self.world.init_state

        # Compute path from start to exit with A*.
        exit_position, exit_cell = self.level.get_exit()
        came_from, cost_so_far, current, n_steps = a_star_search(
            graph=WorldGraph(self.world), start=self.state,
            exit_definition=exit_position,
            extract_definition=self.world.get_player_position)

        search_path = []
        while True:
            if current is None:
                break
            search_path.append(current)
            current = came_from[current]

        for state in search_path:
            self.game_objects.append(Searched(*self.world.get_player_position(state)))

        trajectory_path = self.trajectory.get_path()
        for point in trajectory_path:
            self.game_objects.append(TrajectoryPath(*point))

        # Initialize sprites.
        self.sprites = pygame.sprite.Group(self.game_objects)

    def _initialize_controller(self, controller):
        self.controller = controller

    def _update_display(self):
        self.screen.blit(self.surface, (0, 0))
        self.sprites.update()
        self.menu.draw()
        self.sprites.draw(self.screen)
        pygame.display.flip()
        pygame.display.update()

    def _remove_collected(self):
        for obj in self.game_objects:
            if (type(obj) is Wine or type(obj) is Cheese) and obj.x == self.player.x and obj.y == self.player.y:
                obj.remove()

    def _teardown(self):
        print('Exiting...')
        if self.enginestate.stop_event is not None:
            self.enginestate.stop_event.set()
        pygame.mixer.quit()
        pygame.quit()

    def start(self, mode, level_filename=None):
        self._clear_screen()
        if self.level is None:
            self._load_level(level_filename)
        self._initialize_level()
        self._set_mode(mode)
        self._set_playing(True)

    def _check_new_level(self):
        if self.enginestate.output_queue is not None:
            level = None
            while True:
                # Empty the queue.
                try:
                    level, trajectory = self.enginestate.output_queue.get_nowait()
                except queue.Empty:
                    if self.enginestate.output_queue.empty():
                        break

            if self.enginestate.go_next_level:
                # Load next level.
                if level is None:
                    # No new level this time, but maybe we got an unused one still waiting?
                    if self.last_valid_level is None:
                        return
                    else:
                        level = self.last_valid_level
                assert level is not None
                self.last_valid_level = None
                self.enginestate.go_next_level = False
                print('Going to next level')
                self._load_level(level=level, trajectory=trajectory)
                self.start(self.enginestate.mode)
            elif level is not None:
                # Remember it in case we need it later.
                self.last_valid_level = level

    def loop(self):
        tick = 0
        keys = []
        key = None
        self._play_sound('spawn')
        while True:
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == QUIT:
                    self._teardown()
                    sys.exit()
                if event.type == KEYDOWN:
                    if K_SPACE == event.key:
                        self._teardown()
                        sys.exit()
                    else:
                        if self.enginestate.mode == self.MODE_KEYBOARD:
                            keys.append(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.menu.on_mouse_down()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.menu.on_mouse_up()
                elif event.type == CustomEvents.EVENT_MODE_CHANGED:
                    self.start(event.message)
                elif event.type == CustomEvents.EVENT_GO_NEXT_LEVEL:
                    self.enginestate.go_next_level = True
            if self.enginestate.playing:
                if len(keys) > 0:
                    key = keys.pop(0)
                else:
                    key = None
                action = self.controller.get_action(data=key)
                if action is not None:
                    state = self.world.perform(self.state, action)
                    if state is not None:
                        self.state = state
                        player_pos = self.world.get_player_position(self.state)
                        self.player.x, self.player.y = player_pos
                        self.player.update_coords()
                        self._remove_collected()
                        if self.player.x == self.exit.x and self.player.y == self.exit.y:
                            self._play_sound('win')
                            self._set_playing(False)
                            self.clock.tick(1)
                        else:
                            self._play_sound('move')
                    else:
                        self._play_sound('blocked')
            self.menu.update(self.enginestate)
            self._update_display()
            self.clock.tick(self.TICKS_PER_SECOND)
            tick += 1
            if self.enginestate.mode == self.MODE_ASTAR and not self.enginestate.playing:
                self.enginestate.go_next_level = True
            self._check_new_level()


class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, x_offset=0, y_offset=0):
        self.x = x
        self.y = y
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.update_coords()
        self.killed = False
        super().__init__()

    def update_coords(self):
        self.rect.x = GameEngine.MARGIN_LEFT + self.x * GameEngine.CELL_SIZE + self.x_offset
        self.rect.y = GameEngine.MARGIN_TOP + self.y * GameEngine.CELL_SIZE + self.y_offset

    def remove(self):
        if not self.killed:
            self.killed = True
            self.kill()


# Characters.

class Player(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('player.png', rescale=(GameEngine.CELL_SIZE, GameEngine.CELL_SIZE))
        super().__init__(x, y)


# Obstacles.

class Block(GameObject):
    def __init__(self, x, y):
        name = 'wall%d.png' % (np.random.randint(5) + 1)
        self.image, self.rect = GameUtils.load_image(name, rescale=(GameEngine.CELL_SIZE, GameEngine.CELL_SIZE))
        super().__init__(x, y)


class Ice(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('ice.png', rescale=(GameEngine.CELL_SIZE, GameEngine.CELL_SIZE))
        super().__init__(x, y)


class Tornado(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('tornado.png',
                                                     rescale=(GameEngine.CELL_SIZE, GameEngine.CELL_SIZE))
        super().__init__(x, y)


class Empty(GameObject):
    def __init__(self, x, y):
        # name = 'empty%d.png' % (((x + y) % 2) + 1)
        name = 'empty%d.png' % (((x + y) % 1) + 1)
        self.image, self.rect = GameUtils.load_image(name, rescale=(GameEngine.CELL_SIZE, GameEngine.CELL_SIZE))
        super().__init__(x, y)


# Items.

class Cheese(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('cheese.png', rescale=(GameEngine.CELL_SIZE, GameEngine.CELL_SIZE))
        super().__init__(x, y)


class Wine(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('wine.png', rescale=(GameEngine.CELL_SIZE, GameEngine.CELL_SIZE))
        super().__init__(x, y)


# Objectives.

class Exit(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('exit.png', rescale=(GameEngine.CELL_SIZE, GameEngine.CELL_SIZE))
        super().__init__(x, y)


# Trajectories.

class Searched(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('searched.png', rescale=(3, 3))
        super().__init__(x, y, x_offset=GameEngine.CELL_SIZE//2-1, y_offset=GameEngine.CELL_SIZE//2-1)


class TrajectoryPath(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('trajectory.png', rescale=(6, 6))
        super().__init__(x, y, x_offset=GameEngine.CELL_SIZE//2-3, y_offset=GameEngine.CELL_SIZE//2-3)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        level_filename = sys.argv[1]
    else:
        level_filename = None
    engine = GameEngine(fullscreen=False)
    engine.start(GameEngine.MODE_KEYBOARD, level_filename=level_filename)
    engine.loop()
