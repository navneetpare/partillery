import os
import sys

import pygame
import partillery.utils as utils
from partillery.game.game import Game


class Root:
    context = None
    resolutions = {'480p': (640, 480),
                   '720p': (1280, 720),
                   '1080p': (1920, 1080)}


    @staticmethod
    def handle_exit_key(event: pygame.event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.mixer.quit()
            pygame.display.quit()
            pygame.quit()
            sys.exit()

    def __init__(self):
        pass

    def start(self):
        # Read config
        config = utils.load_config_resource()

        # Init pygame
        resolution = self.resolutions[config.display.resolution]
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (config.display.pos_x, config.display.pos_y)
        pygame.init()
        display_restore_info = pygame.display.Info()
        restore_resolution = (display_restore_info.current_w, display_restore_info.current_h)
        clock = pygame.time.Clock()
        pygame.display.set_caption(config.display.caption)
        screen_mode = pygame.RESIZABLE
        if config.display.fullscreen:
            screen_mode = pygame.FULLSCREEN
        screen = pygame.display.set_mode(resolution, screen_mode)
        pygame.display.set_icon(utils.load_image_resource('window_icon.png'))
        pygame.event.set_allowed([pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION])

        # Launch
        self.context = Game(screen, resolution, restore_resolution, clock, config)
        self.context.run()
