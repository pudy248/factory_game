import pygame as pg
import sys, os

os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
clock = pg.time.Clock()
W = pg.display.Info().current_w
H = pg.display.Info().current_h
SURF = pg.display.set_mode((W, H), pg.NOFRAME)

#####CONSTANTS#####
FPS = 60
TILE_SIZE = 50  # dimensions of each tile in pixels
#####################


class Tile:
    def __init__(self, pos):
        self.pos = pos
        self.direction = [0, 0]
        self.image = pg.transform.scale(pg.image.load("pacman.png"), (TILE_SIZE, TILE_SIZE))
        self.resource = "None"  # None, Iron, Wood, Coal, Oil, Out of Bounds
        self.type = "Tile"
        self.items = []

    def draw(self):
        SURF.blit(self.image, (self.pos[0] * TILE_SIZE, self.pos[1] * TILE_SIZE))

    def tick(self):
        pass  # empty for now, not sure what to put in the generic tile class since it is never used in-game

    def is_open(self, type):
        if self.resource is "Out of Bounds":
            return False
        elif self.resource is not None and type != "Extractor":
            return False
        return True


while True:
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
    pg.display.update()
    clock.tick(FPS)