from pygame.sprite import DirtySprite


class Player(DirtySprite):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.power = 0
        self.score = 0
        self.turret = None