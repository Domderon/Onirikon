#!/usr/bin/env pythonw

import os
import random
import sys

# Initialize seed immediately to be safe (default = system clock, but you can use a fixed integer for debugging).
random.seed(None)

import pygame
from pygame.locals import QUIT, K_SPACE, KEYDOWN

from controllers import KeyboardController
from game_utils import GameUtils
from level import Level, EmptyCell, BlockCell, StartPositionCell, ExitCell
from search import WorldGraph, a_star_search
from trajectory import Trajectory
from world import World


class GameEngine:
    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 768
    CELL_SIZE = 20
    TICKS_PER_SECOND = 60
    ACTION_INTERVAL_TICKS = 1
    SOUNDS = ['spawn', 'move', 'blocked', 'drink', 'eat', 'win']

    def init_display(self, fullscreen):
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        surface = pygame.Surface(self.screen.get_size())
        self.surface = surface.convert()
        self.surface.fill((255, 255, 255))

    def init_clock(self):
        self.clock = pygame.time.Clock()

    def init_keyboard(self):
        pygame.key.set_repeat(1, 40)

    def init_sound(self):
        self.sounds = {}
        for name in self.SOUNDS:
            try:
                self.sounds[name] = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'assets', 'sound',
                                                                    name + '.wav'))
            except FileNotFoundError:
                print('Warning: sound "%s" not found' % name)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def __init__(self, fullscreen=False):
        pygame.init()
        self.init_display(fullscreen)
        self.init_keyboard()
        self.init_clock()
        self.init_sound()

    def initialize_level(self, level_filename=None):
        if level_filename is None:
            self.level = Level(40, 30)
            trajectory = Trajectory(self.level)
            self.level.generate_from_trajectory(trajectory, 0.2)
        else:
            self.level = Level.load_level(level_filename)
        self.level_width, self.level_height = self.level.size()
        self.game_objects = []
        for x in range(self.level_width):
            for y in range(self.level_height):
                cell = self.level.get_cell(x, y)
                if type(cell) is EmptyCell:
                    obj = None
                elif type(cell) is BlockCell:
                    obj = Block(x, y)
                elif type(cell) is StartPositionCell:
                    obj = Player(x, y)
                    self.player = obj
                elif type(cell) is ExitCell:
                    obj = Exit(x, y)
                    self.exit = obj
                else:
                    obj = None
                if obj is not None:
                    self.game_objects.append(obj)

        self.world = World(self.level)
        self.state = self.world.init_state

        # Compute path from start to exit with A*.
        exit_position, exit_cell = self.level.get_exit()
        came_from, cost_so_far, current = a_star_search(
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

        trajectory_path = trajectory.get_path()
        for point in trajectory_path:
            self.game_objects.append(TrajectoryPath(*point))

        # Initialize sprites.
        self.sprites = pygame.sprite.Group(self.game_objects)

    def initialize_controller(self, controller):
        self.controller = controller

    def update_display(self):
        self.screen.blit(self.surface, (0, 0))
        self.sprites.update()
        self.sprites.draw(self.screen)
        pygame.display.flip()
        pygame.display.update()

    def teardown(self):
        pygame.mixer.quit()
        pygame.quit()

    def loop(self):
        tick = 0
        keys = []
        self.play_sound('spawn')
        while True:
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.teardown()
                    sys.exit()
                if event.type == KEYDOWN:
                    if K_SPACE == event.key:
                        self.teardown()
                        sys.exit()
                    else:
                        keys.append(event)
            if tick % self.ACTION_INTERVAL_TICKS == 0:
                while len(keys) > 0:
                    key = keys.pop(0)
                    action = self.controller.get_action(data=key)
                    if action is not None:
                        state = self.world.perform(self.state, action)
                        if state is not None:
                            self.state = state
                            player_pos = self.world.get_player_position(self.state)
                            self.player.x, self.player.y = player_pos
                            self.player.update_coords()
                            if self.player.x == self.exit.x and self.player.y == self.exit.y:
                                print("WIN")
                                self.play_sound('win')
                                self.clock.tick(1)
                            else:
                                self.play_sound('move')
                        else:
                            self.play_sound('blocked')
                        break
            self.update_display()
            self.clock.tick(self.TICKS_PER_SECOND)
            tick += 1


class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.update_coords()
        super().__init__()

    def update_coords(self):
        self.rect.x = self.x * GameEngine.CELL_SIZE
        self.rect.y = self.y * GameEngine.CELL_SIZE


class Block(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('block.png')
        super().__init__(x, y)


class Player(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('player.png')
        super().__init__(x, y)


class Exit(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('exit.png')
        super().__init__(x, y)


class Searched(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('searched.png', rescale=(3, 3))
        super().__init__(x, y)

class TrajectoryPath(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('trajectory.png', rescale=(6, 6))
        super().__init__(x, y)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        level_filename = sys.argv[1]
    else:
        level_filename = None
    engine = GameEngine(fullscreen=False)
    engine.initialize_level(level_filename)
    engine.initialize_controller(KeyboardController())
    engine.loop()
