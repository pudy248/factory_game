import pygame as pg
import sys, os

os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
clock = pg.time.Clock()
W = pg.display.Info().current_w
H = pg.display.Info().current_h
SURF = pg.display.set_mode((W, H), pg.NOFRAME)
img = pg.image.load('pacman.png')

#####CONSTANTS#####
FPS = 60
TILE_SIZE = 50  # dimensions of each tile in pixels
#####################

class Level:
    def __init__(self, tMap):
        self.map = tMap

    def world_tick(self):
        x = 4  # placeholder

    def draw_level(self):
        side = len(self.map)
        for tiley in range(side):
            for tilex in range(side):
                if self.map[tiley][tilex] == "1":
                    SURF.blit(img, ((side-tilex - 1) * TILE_SIZE, tiley * TILE_SIZE))

class Loader:
    def __init__(self):
        self.lNum = 0

    def load_level(self, n):
        self.lNum = n
        text = 'levels/' + str(n) + '.txt'
        lines = []
        map = []
        with open(text, 'rt') as myfile:
            for line in myfile:
                lines.append(line.rstrip(" \n"))
        for i in range(len(lines)):
            map.append([])
        for i in range(len(map)):
            map[i] = lines[i].split(" ")
        return Level(map)

while True:
    load = Loader()
    lvl = load.load_level(0)  # 0.txt is just a dummy for testing
    lvl.draw_level()
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
    pg.display.update()
    clock.tick(FPS)
