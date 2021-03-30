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
#####################


class Player:
    def __init__(self):
        self.selected_tile = False
        self.last_pos = (0, 0)

    def is_in_level(self):  # Detects if pos is within the level
        return self.last_pos[1] < 300

    def can_place(self):
        return self.selected_tile and self.get_tile().replacable

    def can_select(self):
        if self.get_tile:
            return True
        return False

    def get_tile(self):
        return level.tiles[self.last_pos[1]//10][self.last_pos[0]//10]

    def click(self, pos):
        self.last_pos = pos
        if self.is_in_level():
            if self.can_place():
                self.place(self.selected_tile)
        elif self.can_select():
            self.selected_tile = self.get_tile()


while True:
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
    clock.tick(FPS)