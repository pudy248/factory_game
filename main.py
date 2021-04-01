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

class Level:
    def __init__(self, tMap):
        self.map = tMap

    def world_tick(self):
        x = 4  # placeholder

    def draw_level(self):
        side = len(self.map)
        for tiley in range(side):
            for tilex in range(side):
                self.map[tiley][tilex].draw()

class Loader:
    def __init__(self):
        self.lNum = 0

    def load_level(self, n):
        self.lNum = n
        text = 'levels/' + str(n) + '.txt'
        lines = []
        tMap = []
        with open(text, 'rt') as myfile:
            for line in myfile:
                lines.append(line.rstrip(" \n"))
        for i in range(len(lines)):
            tMap.append([])
        for i in range(len(tMap)):
            tMap[i] = lines[i].split(" ")
        lvl = self.convert(tMap)
        return lvl

    def convert(self, tMap):
        side = len(tMap)
        newMap = []
        for i in range(side):
            newMap.append([Tile([0, 0])] * side)
        for y in range(side):
            for x in range(side):
                pos = [y, x]
                print(pos)
                newMap[y][x] = Tile(pos)
        return Level(newMap)

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
