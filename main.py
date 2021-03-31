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
        self.type = "Tile"
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


class Player:
    def __init__(self):
        self.selected_tile = False
        self.last_pos = (0, 0)

    def is_in_level(self):  # Detects if pos is within the level
        return self.last_pos[0] < TILE_SIZE*len(lvl.map[0]) and self.last_pos[1] < TILE_SIZE*len(lvl.map)

    def can_place(self):  # should work
        return self.selected_tile and self.get_tile().is_open(self.selected_tile.type)

    def get_tile(self):  # works
        return lvl.map[self.last_pos[1]//TILE_SIZE][self.last_pos[0]//TILE_SIZE]

    def place(self):  # works
        self.selected_tile.pos = ((self.last_pos[0]//TILE_SIZE)*TILE_SIZE, (self.last_pos[1]//TILE_SIZE)*TILE_SIZE)
        lvl.map[self.last_pos[1]//TILE_SIZE][self.last_pos[0]//TILE_SIZE] = self.selected_tile

    def click(self, pos):
        self.last_pos = pos
        if self.is_in_level():
            if self.can_place():
                self.place()

    def select(self, key):
        if key == pg.K_1:
            self.selected_tile = Tile(self.last_pos)

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

class Level:
    def __init__(self, map):
        self.map = map

    def world_tick(self):
        x = 4 # placeholder

    def draw_level(self):
        print(self.map) # just for testing

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


load = Loader()
lvl = load.load_level(0) # 0.txt is just a dummy for testing
player = Player()
while True:
    # lvl.draw_level() # only here to test that the file was parsed properly
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            player.select(event.key)
        elif event.type == pg.MOUSEBUTTONUP:
            player.click(event.pos)
    pg.display.update()
    clock.tick(FPS)
