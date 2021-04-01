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

class Item:
    def __init__(self, name):
        self.name = name
        self.image = None
        self.direction = [0, 0]
        self.moved = False

class Tile:
    def __init__(self, pos):
        self.pos = pos
        self.direction = [1, 0]
        self.image = pg.transform.scale(pg.image.load("pacman.png"), (TILE_SIZE, TILE_SIZE))
        self.resource = "None"  # None, Iron, Wood, Coal, Oil, Out of Bounds
        self.items = []

    def draw(self):
        SURF.blit(pg.transform.rotate(self.image, 180 if self.direction[0] == -1 else (180 - 90 * self.direction[1])), (self.pos[0] * TILE_SIZE, self.pos[1] * TILE_SIZE))

    def tick(self):
        # Every tile has the ability to move items
        for i in range(len(self.items)):
            if self.items[i].moved:
                continue
            temp = self.items.pop(i)
            i -= 1
            temp.direction = self.direction
            temp.moved = True
            level.tile_array[self.pos[0] + self.direction[0]][self.pos[1] + self.direction[1]].items.append(temp)

    def is_open(self, type):
        if self.resource == "Out of Bounds":
            return False
        elif self.resource is not None and type != "Extractor":
            return False
        return True

class Level:
    def __init__(self, tMap):
        self.map = tMap
        self.side = len(self.map)

    def world_tick(self):
        for tiley in range(self.side):
            for tilex in range(self.side):
                self.map[tiley][tilex].tick()

    def draw_level(self):
        for tiley in range(self.side):
            for tilex in range(self.side):
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

class Extractor(Tile):
    def __init__(self, pos):
        super().__init__(pos)
        self.type = "Extractor"

    def tick(self):
        # adds an item based on resources
        super(Extractor, self).tick()

class Manufacturer(Tile):
    def __init__(self, pos):
        super().__init__(pos)
        self.type = "Manufacturer"

    def tick(self):
        # if Recipie Collection class says that the items in self.items can be made into a recipie, consumes them and outputs the result
        super(Manufacturer, self).tick()

level = None  # Level class, overwritten when the loader is called

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
    pg.display.update()
    clock.tick(FPS)