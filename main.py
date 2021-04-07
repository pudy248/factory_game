import pygame as pg
import sys, os, time

os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
clock = pg.time.Clock()
W = pg.display.Info().current_w
H = pg.display.Info().current_h
SURF = pg.display.set_mode((W, H), pg.NOFRAME)

#####CONSTANTS#####
FPS = 60
TILE_SIZE = 100  # dimensions of each tile in pixels
TICK_RATE = 10  # ticks per second
#####################


class Level:
    def __init__(self, tMap):
        self.tile_array = tMap
        self.side = len(self.tile_array)

    def world_tick(self):
        for tiley in range(self.side):
            for tilex in range(self.side):
                for i in self.tile_array[tiley][tilex].items:
                    i.moved = False
        for tiley in range(self.side):
            for tilex in range(self.side):
                self.tile_array[tiley][tilex].tick()

    def draw_level(self):
        for tiley in range(self.side):
            for tilex in range(self.side):
                self.tile_array[tiley][tilex].draw()


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
            newMap.append([Tile([0, 0], 0)] * side)
        for y in range(side):
            for x in range(side):
                pos = [x, y]
                str = tMap[y][x]
                if str == '+':
                    newMap[y][x] = Intersection(pos, 0)
                    newMap[y][x].image = pg.transform.scale(pg.image.load("sprites\\tile_x_conveyor.png"), (TILE_SIZE, TILE_SIZE))
                else:
                    angle = 0 if str == '>' else (90 if str == '^' else (180 if str == '<' else 270))
                    newMap[y][x] = Belt(pos, angle)
        return Level(newMap)


class Item:
    def __init__(self, name):
        self.name = name
        self.image = pg.image.load("sprites\\tile_grass.png")
        self.direction = pg.Vector2([0, 1])
        self.moved = False
        self.offset = 0


class Tile:
    def __init__(self, pos, angle):
        self.pos = pos
        self.direction = pg.Vector2([1, 0]).rotate(angle)
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_conveyor.png"), (TILE_SIZE, TILE_SIZE))
        self.resource = "None"  # None, Iron, Wood, Coal, Oil, Out of Bounds
        self.type = "Tile"
        self.items = []

    def draw(self):
        SURF.blit(pg.transform.rotate(self.image, -self.direction.angle_to(pg.Vector2([1, 0]))), (self.pos[0] * TILE_SIZE, self.pos[1] * TILE_SIZE))

    def tick(self):
        if self.type != "Tile":
            i = 0
            while i < len(self.items):
                if self.items[i].moved:
                    i += 1
                else:
                    i += 1



    def is_open(self, type):
        if self.resource == "Out of Bounds":
            return False
        elif self.resource != "None" and type != "Extractor":
            return False
        return True


class Extractor(Tile):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Extractor"

    def tick(self):
        # adds an item based on resources
        super(Extractor, self).tick()
        self.items.append(Item(self.resource))


class Manufacturer(Tile):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Manufacturer"

    def tick(self):
        # if Recipie Collection class says that the items in self.items can be made into a recipie, consumes them and outputs the result
        super(Manufacturer, self).tick()
        # TODO implement this


class Belt(Tile):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Belt"


class Intersection(Belt):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Intersection"

    def tick(self):
        # Respects item direction
        i = 0
        while i < len(self.items):
            if self.items[i].moved:
                i += 1
            else:
                i += 1


class Splitter(Belt):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Splitter"
        self.split_bool = False  # False = right, True = left

    def tick(self):
        # Alternates between left and right
        # TODO doesn't work for some reason
        i = 0
        while i > len(self.items):
            if self.items[i].moved:
                i += 1
            else:
                i += 1



t  = time.perf_counter()
dt = 0
level = Loader().load_level(0)
level.tile_array[0][0].items.append(Item("Iron"))
level.tile_array[1][0].items.append(Item("Iron"))
while True:
    level.world_tick()
    level.draw_level()
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
    pg.display.update()
    clock.tick(FPS)
