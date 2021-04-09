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
TICK_RATE = 2  # ticks per second
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
                    if self.tile_array[tiley][tilex].type == "Splitter":
                        i.direction = self.tile_array[tiley][tilex].direction.rotate(90 if self.tile_array[tiley][tilex].split_bool else 270)
                    else:
                        i.direction = self.tile_array[tiley][tilex].direction
        for tiley in range(self.side):
            for tilex in range(self.side):
                self.tile_array[tiley][tilex].tick()

    def draw_level(self):
        for tiley in range(self.side):
            for tilex in range(self.side):
                self.tile_array[tiley][tilex].draw()
        for tiley in range(self.side):
            for tilex in range(self.side):
                if self.tile_array[tiley][tilex].type == "Belt" and len(self.tile_array[tiley][tilex].items) > 0:
                    for i in self.tile_array[tiley][tilex].items:
                        img = pg.transform.scale(i.image, (int(TILE_SIZE / 2), int(TILE_SIZE / 2)))
                        SURF.blit(img, (self.tile_array[tiley][tilex].pos[0] * TILE_SIZE + TILE_SIZE / 4 +
                            (i.offset * i.direction[0] * TILE_SIZE), self.tile_array[tiley][tilex].pos[1] * TILE_SIZE + TILE_SIZE / 4 - (i.offset * i.direction[1] * TILE_SIZE)))

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
                elif str in ["<", ">", "^", "v"]:
                    angle = 0 if str == '>' else (90 if str == '^' else (180 if str == '<' else 270))
                    newMap[y][x] = Belt(pos, angle)
                else:
                    newMap[y][x] = Tile(pos, 0)
        return Level(newMap)


class Item:
    def __init__(self, name):
        self.name = name
        self.image = pg.image.load("sprites\\tile_grass.png")
        self.direction = pg.Vector2([0, 1])
        self.moved = True
        self.offset = 0


class Recipe:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

    def check_inputs(self, inputs):
        if len(inputs) != len(self.inputs):
            return False
        else:
            for i in inputs:
                contained = False
                for j in self.inputs:
                    if i == j:
                        contained = True
                if not contained:
                    return False
        return True


class Recipe_Collection:
    def __init__(self, recipes):
        self.recipes = []
        self.recipes.extend(recipes)

    def get_recipe(self, inputs):
        for r in self.recipes:
            if r.check_inputs(inputs):
                return r
        return False


class Tile:
    def __init__(self, pos, angle):
        self.pos = pos
        self.direction = pg.Vector2([1, 0]).rotate(angle)
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_forest.png"), (TILE_SIZE, TILE_SIZE))
        self.resource = "None"  # None, Iron, Wood, Coal, Oil, Out of Bounds
        self.type = "Tile"
        self.items = []

    def __str__(self):
        return str(self.type) + ": " + str(self.pos)

    def draw(self):
        SURF.blit(pg.transform.rotate(self.image, -self.direction.angle_to(pg.Vector2([1, 0]))), (self.pos[0] * TILE_SIZE, self.pos[1] * TILE_SIZE))

    def tick(self):
        if self.type != "Tile":
            for i in self.items:
                i.offset += TICK_RATE / FPS
            i = 0
            while i < len(self.items):
                if not self.items[i].moved and self.items[i].offset > 1 and \
                       -1 < int(self.pos[1] - self.items[i].direction.y) < len(level.tile_array) and -1 < int(self.pos[0] + self.items[i].direction.x) < len(level.tile_array[0]):
                    temp = self.items.pop(i)
                    temp.moved = True
                    temp.offset -= 1
                    level.tile_array[int(self.pos[1] - temp.direction.y)][int(self.pos[0] + temp.direction.x)].items.append(temp)
                else:
                    i += 1



    def is_open(self, type):
        if self.resource == "Out of Bounds":
            return False
        elif self.resource != "None" and type != "Extractor":
            return False
        return True


class Player:
    def __init__(self):
        self.selected_tile = False
        self.tile_angle = 0
        self.last_pos = [0, 0]

    def is_in_level(self):  # Detects if pos is within the level
        return self.last_pos[0] < TILE_SIZE * len(level.tile_array[0]) and self.last_pos[1] < TILE_SIZE * len(level.tile_array)

    def can_place(self):  # should work
        return self.selected_tile and self.get_tile().is_open(self.selected_tile)

    def get_tile(self):  # works
        return level.tile_array[self.last_pos[1] // TILE_SIZE][self.last_pos[0] // TILE_SIZE]

    def place(self):  # works
        if self.selected_tile == "Extractor":
            level.tile_array[self.last_pos[1] // TILE_SIZE][self.last_pos[0] // TILE_SIZE] = Extractor([(self.last_pos[0]//TILE_SIZE), (self.last_pos[1]//TILE_SIZE)], 0)
        elif self.selected_tile == "Manufacturer":
            level.tile_array[self.last_pos[1] // TILE_SIZE][self.last_pos[0] // TILE_SIZE] = Manufacturer([(self.last_pos[0]//TILE_SIZE), (self.last_pos[1]//TILE_SIZE)], 0)
        elif self.selected_tile == "Belt":
            level.tile_array[self.last_pos[1] // TILE_SIZE][self.last_pos[0] // TILE_SIZE] = Belt([(self.last_pos[0]//TILE_SIZE), (self.last_pos[1]//TILE_SIZE)], self.tile_angle)
        elif self.selected_tile == "Intersection":
            level.tile_array[self.last_pos[1] // TILE_SIZE][self.last_pos[0] // TILE_SIZE] = Intersection([(self.last_pos[0]//TILE_SIZE), (self.last_pos[1]//TILE_SIZE)], self.tile_angle)
        elif self.selected_tile == "Splitter":
            level.tile_array[self.last_pos[1] // TILE_SIZE][self.last_pos[0] // TILE_SIZE] = Splitter([(self.last_pos[0]//TILE_SIZE), (self.last_pos[1]//TILE_SIZE)], self.tile_angle)
        elif self.selected_tile == "Tile":
            level.tile_array[self.last_pos[1] // TILE_SIZE][self.last_pos[0] // TILE_SIZE] = Tile([(self.last_pos[0]//TILE_SIZE), (self.last_pos[1]//TILE_SIZE)], self.tile_angle)

    def click(self, pos):
        self.last_pos = pos
        if self.is_in_level():
            if self.can_place():
                self.place()

    def select(self, key):
        if key == pg.K_1:
            self.selected_tile = "Extractor"
        elif key == pg.K_2:
            self.selected_tile = "Manufacturer"
        elif key == pg.K_3:
            self.selected_tile = "Belt"
        elif key == pg.K_4:
            self.selected_tile = "Intersection"
        elif key == pg.K_5:
            self.selected_tile = "Splitter"
        elif key == pg.K_6:
            self.selected_tile = "Tile"
        elif key == pg.K_r:
            self.tile_angle = (self.tile_angle - 90) % 360

class Extractor(Tile):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Extractor"
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_grass.png"), (TILE_SIZE, TILE_SIZE))

    def tick(self):
        # adds an item based on resources
        super(Extractor, self).tick()
        self.items.append(Item(self.resource))

class Manufacturer(Tile):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Manufacturer"
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_factory.png"), (TILE_SIZE, TILE_SIZE))

    def tick(self):
        # if Recipie Collection class says that the items in self.items can be made into a recipie, consumes them and outputs the result
        super(Manufacturer, self).tick()
        # TODO implement this


class Belt(Tile):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Belt"
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_conveyor.png"), (TILE_SIZE, TILE_SIZE))


class Intersection(Belt):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Intersection"
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_x_conveyor.png"), (TILE_SIZE, TILE_SIZE))

    def tick(self):
        for i in self.items:
            i.offset += TICK_RATE / FPS
        i = 0
        while i < len(self.items):
            if not self.items[i].moved and self.items[i].offset > 1 and \
                    -1 < int(self.pos[1] - self.items[i].direction.y) < len(level.tile_array) and -1 < int(self.pos[0] + self.items[i].direction.x) < len(level.tile_array[0]):
                temp = self.items.pop(i)
                temp.moved = True
                temp.offset -= 1
                level.tile_array[int(self.pos[1] - temp.direction.y)][int(self.pos[0] + temp.direction.x)].items.append(temp)
            else:
                i += 1


class Splitter(Belt):
    def __init__(self, pos, angle):
        super().__init__(pos, angle)
        self.type = "Splitter"
        self.split_bool = False  # False = right, True = left
    def tick(self):
        # Alternates between left and right
        # TODO doesn't work for some reason, don't use
        for i in self.items:
            i.offset += TICK_RATE / FPS
        i = 0
        while i > len(self.items):
            if not self.items[i].moved and self.items[i].offset > 1:
                self.split_bool = not self.split_bool
                temp = self.items.pop(i)

                temp.moved = True
                temp.offset -= 1
                level.tile_array[int(self.pos[1] - temp.direction.y)][int(self.pos[0] + temp.direction.x)].items.append(temp)
            else:
                i += 1


rc = Recipe_Collection((Recipe(("Wood", "Iron Ore"), ("Iron Bar")), Recipe(("Natural Gas", "Iron Ore"), ("Iron Bar")),
                        Recipe(("Coal", "Iron Bar"), ("Steel Bar")), Recipe(("Iron Bar"), ("Iron Tubes")), Recipe(("Iron Tubes"), ("Screws")),
                        Recipe(("Steel Bar"), ("Steel Tubes")), Recipe(("Steel Bar", "Iron Bar"), ("Alloy Plate")),
                        Recipe(("Steel Tubes"), ("Springs")), Recipe(("Screws", "Springs"), ("Machine Parts")),
                        Recipe(("Alloy Plate", "Machine Parts", "Steel Tubes"), ("Engines")), Recipe(("Engines", "Springs", "Coal"), ("Locomotives")),
                        Recipe(("Engines", "Alloy Plate", "Gasoline"), ("Automobiles")), Recipe(("Steel Tubes", "Plastic"), ("Consumer Goods")),
                        Recipe(("Oil"), ("Natural Gas", "Petroleum")), Recipe(("Petroleum"), ("Plastic", "Gasoline"))))
load = Loader()
level = load.load_level(0) # 0.txt is just a dummy for testing
level.tile_array[0][0].items.append(Item(""))
player = Player()
while True:
    level.world_tick()
    SURF.fill((0, 0, 0))
    level.draw_level()
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
