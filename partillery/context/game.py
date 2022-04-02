import time

import pygame

from partillery.controls import ControlPanel


class Game:

    def __init__(self, screen, clock, config):
        self.name = "Game"
        self.MODE_CONTROL = "Control"
        self.MODE_FLIGHT = "Flight"
        self.MODE_TEST = "Test"
        self.screen = screen
        self.clock = clock
        self.config = config
        self.mode = self.MODE_CONTROL

    def run(self):
        # Alias key params so I don't have to type 'self' everywhere.
        screen = self.screen
        clock = self.clock
        config = self.config

        # Game window dims and coordinates (height, width, left edge, right edge, top edge, bottom edge)
        h = int(config.display.height * config.game_area.height_fraction)
        w = config.display.width
        l = 0
        r = w
        t = 0
        b = h

        # Control panel dims and coordinates (height, width, left edge, right edge, top edge, bottom edge)
        ch = config.display.height - h
        cw = w
        cl = 0
        cr = r
        ct = h
        cb = config.display.height
        c_bg_img = config.game_control_panel.background_img

        cpl = ControlPanel(screen, cl, ct, cw, ch, c_bg_img)

        while True:
            time.sleep(1)
            pygame.display.update()
            clock.tick(60)
