import os
import pygame
from binascii import crc32
from numpy import random


class GameUtils:
    DEFAULT_WIDTH = 20
    DEFAULT_HEIGHT = 20

    def _color_from_string(s):
        h = crc32(s.encode('utf-8'))
        color = (h % 256, (h//256) % 256, (h//65536) % 256)
        return color

    def generate_placeholder_image(name):
        image = pygame.Surface((GameUtils.DEFAULT_WIDTH, GameUtils.DEFAULT_HEIGHT))
        rect = pygame.Rect(random.randint(1000), random.randint(700), GameUtils.DEFAULT_WIDTH, GameUtils.DEFAULT_HEIGHT)
        color = GameUtils._color_from_string(name)
        image.fill(color)
        return image, rect

    def load_image(name, rescale=None):
        fullname = os.path.join('assets', 'images', name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error:
            print('Warning: cannot load image: %s, generating placeholder' % fullname)
            return GameUtils.generate_placeholder_image(name)
        if rescale is not None:
            image = pygame.transform.scale(image, rescale)
        return image.convert(), image.get_rect()
