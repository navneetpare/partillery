import os
import pygame

import partillery.utils as utils
from partillery.context.game import Game


class Root:
    context = None

    def __init__(self):
        pass

    def start(self):
        # Read config
        config = utils.load_config_resource("___game_settings.yaml")

        # Init pygame
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (config.display.pos_x, config.display.pos_y)
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption(config.display.caption)
        # pygame.display.set_icon(pygame.image.load(utils.load_image_resource('window_icon')))
        screen = pygame.display.set_mode((config.display.width, config.display.height), pygame.RESIZABLE)

        # Launch
        self.context = Game(screen, clock, config)
        self.context.run()
