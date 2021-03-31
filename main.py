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

class Level:
    def __init__(self, map):
        self.map = map

    def world_tick(self):
        x = 4  # placeholder

    def draw_level(self):
        print(self.map)  # just for testing

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
    lvl.draw_level()  # only here to test that the file was parsed properly
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
    pg.display.update()
    clock.tick(FPS)
