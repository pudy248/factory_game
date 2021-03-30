import pygame as pg
import sys, os

os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
clock = pg.time.Clock()
W = pg.display.Info().current_w
H = pg.display.Info().current_h
SURF = pg.display.set_mode((W, H), pg.NOFRAME)

#####CONSTANTS#####
FPS = 5
TILE_SIZE = 100  # dimensions of each tile in pixels
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
                pos = [y, x]
                print(pos)
                newMap[y][x] = Tile(pos, 0)
        return Level(newMap)


class Item:
    def __init__(self, name):
        self.name = name
        self.image = pg.image.load("sprites\\tile_grass.png")
        self.direction = pg.Vector2([0, 1])
        self.moved = False


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
        # Every tile has the ability to move items
        print("1", self.items, self.pos)
        i = 0
        while i < len(self.items):
            if self.items[i].moved:
                i += 1
            else:
                temp = self.items.pop(i)
                print("2", self.items)
                temp.direction = self.direction
                temp.moved = True
                level.tile_array[int(self.pos[0] + self.direction.x)][int(self.pos[1] + self.direction.y)].items.append(temp)
                print("3", self.items)
        print("end")

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
        return self.last_pos[1] < 300

    def can_place(self):
        return self.selected_tile and self.get_tile().is_open(self.selected_tile.type)

    def can_select(self):
        if self.get_tile:
            return True
        return False

    def get_tile(self):
        return level.tiles[self.last_pos[1]//TILE_SIZE][self.last_pos[0]//TILE_SIZE]

    def place(self):
        level.tiles[self.last_pos[1]//TILE_SIZE][self.last_pos[0]//TILE_SIZE] = self.selected_tile

    def click(self, pos):
        self.last_pos = pos
        if self.is_in_level():
            if self.can_place():
                self.place()
        elif self.can_select():
            self.selected_tile = self.get_tile()

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

    def draw(self):
        super(Belt, self).draw()
        if len(self.items) > 0:
            img = pg.transform.scale(self.items[0].image, (int(TILE_SIZE / 2), int(TILE_SIZE / 2)))
            SURF.blit(img, (self.pos[0] * TILE_SIZE + TILE_SIZE / 4, self.pos[1] * TILE_SIZE + TILE_SIZE / 4))


class Intersection(Tile):
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
                temp = self.items.pop(i)
                temp.moved = True
                level.tile_array[int(self.pos[0] + temp.direction.x)][int(self.pos[1] + temp.direction.y)].items.append(temp)


class Splitter(Tile):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Splitter"
        self.split_bool = False  # False = right, True = left
    def tick(self):
        # Alternates between left and right
        i = 0
        while i > len(self.items):
            if self.items[i].moved:
                i += 1
            else:
                self.split_bool = not self.split_bool
                temp = self.items.pop(i)
                direction = pg.Vector2(self.direction[0], self.direction[1])
                temp.direction = direction.rotate(90 if self.split_bool else 270)
                temp.moved = True
                level.tile_array[int(self.pos[0] + temp.direction.x)][int(self.pos[1] + temp.direction.y)].items.append(temp)
level = None  # Level class, overwritten when the loader is called

while True:
    load = Loader()
    lvl = load.load_level(0)
    lvl.draw_level()
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
    pg.display.update()
    clock.tick(FPS)