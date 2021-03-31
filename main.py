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


class Player:
    def __init__(self):
        self.selected_tile = False
        self.last_pos = (0, 0)

    def is_in_level(self):  # Detects if pos is within the level
        return self.last_pos[0] < TILE_SIZE*len(lvl.map[0]) and self.last_pos[1] < TILE_SIZE*len(lvl.map)

    def can_place(self):  # should work
        return self.selected_tile and self.get_tile().is_open(self.selected_tile.type)

    def can_select(self):
        if self.get_tile:
            return True
        return False

    def get_tile(self):  # works
        return lvl.map[self.last_pos[1]//TILE_SIZE][self.last_pos[0]//TILE_SIZE]

    def place(self):  # works
        lvl.map[self.last_pos[1]//TILE_SIZE][self.last_pos[0]//TILE_SIZE] = self.selected_tile

    def click(self, pos):
        self.last_pos = pos
        if self.is_in_level():
            if self.can_place():
                self.place()
        elif self.can_select():
            self.selected_tile = self.get_tile()


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
    lvl.draw_level() # only here to test that the file was parsed properly
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
    pg.display.update()
    clock.tick(FPS)
