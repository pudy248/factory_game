import math
import os
import sys
import time
import math

import pygame as pg

os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
clock = pg.time.Clock()
W = pg.display.Info().current_w
H = pg.display.Info().current_h
SURF = pg.display.set_mode((W, H), pg.NOFRAME)

#####CONSTANTS#####
FPS = 60
TILE_SIZE = 100  # dimensions of each tile in pixels
TICK_RATE = 1  # ticks per second
#####################


class Level:
    def __init__(self, tMap, g, n):
        self.number = n
        self.tile_array = tMap
        self.length = len(self.tile_array)
        self.width = len(self.tile_array[0])
        self.goal = g
        self.surf = pg.Surface([0, 0])
        self.dirty = True

    def world_tick(self):
        for tiley in range(self.length):
            for tilex in range(self.width):
                self.tile_array[tiley][tilex].tick()

    def draw_level(self):
        if self.dirty:
            self.dirty = False
            self.surf = pg.Surface([len(self.tile_array[0]) * TILE_SIZE, self.length * TILE_SIZE])
            for tiley in range(self.length):
                width = len(self.tile_array[tiley])
                for tilex in range(width):
                    self.tile_array[tiley][tilex].blit(self.surf)
                    if self.tile_array[tiley][tilex].type == "Exit":
                        ex = self.tile_array[tiley][tilex]
                        gl = Item(self.goal)
                        img = pg.transform.scale(gl.image, (int(TILE_SIZE / 2), int(TILE_SIZE / 2)))
                        img.fill((255, 255, 255, 185), None, pg.BLEND_RGBA_MULT)
                        self.surf.blit(img, (
                            ex.pos[0] * TILE_SIZE + TILE_SIZE / 2 + (gl.offset * gl.direction[0] * TILE_SIZE),
                            ex.pos[1] * TILE_SIZE + TILE_SIZE / 2 - (gl.offset * gl.direction[1] * TILE_SIZE)))
                    elif self.tile_array[tiley][tilex].resource in ["Wood", "Coal", "Iron Ore", "Oil"]:
                        ex = self.tile_array[tiley][tilex]
                        gl = Item(ex.resource)
                        img = pg.transform.scale(gl.image, (int(TILE_SIZE / 2), int(TILE_SIZE / 2)))
                        img.fill((255, 255, 255, 185), None, pg.BLEND_RGBA_MULT)
                        self.surf.blit(img, (
                            ex.pos[0] * TILE_SIZE + TILE_SIZE / 2 + (gl.offset * gl.direction[0] * TILE_SIZE),
                            ex.pos[1] * TILE_SIZE + TILE_SIZE / 2 - (gl.offset * gl.direction[1] * TILE_SIZE)))
        SURF.blit(self.surf,
                  [(SURF.get_width() - self.surf.get_width()) / 2, (SURF.get_height() - self.surf.get_height()) / 2])
        for tiley in range(self.length):
            for tilex in range(self.width):
                if self.tile_array[tiley][tilex].type == "Belt" or len(
                        self.tile_array[tiley][tilex].items) > 0:  # change back to and
                    for i in self.tile_array[tiley][tilex].items:
                        img = pg.transform.scale(i.image, (int(TILE_SIZE / 2), int(TILE_SIZE / 2)))
                        SURF.blit(img, (self.tile_array[tiley][tilex].get_x() + TILE_SIZE / 4 +
                                        (i.offset * i.direction[0] * TILE_SIZE),
                                        self.tile_array[tiley][tilex].get_y() + TILE_SIZE / 4 - (
                                                i.offset * i.direction[1] * TILE_SIZE)))

    def next_level(self):
        global load
        return load.load_level(self.number + 1)


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
        g = ""
        gArr = tMap[len(tMap) - 1]
        for i in range(len(gArr)):
            if not i == 0:
                g += " "
            g += gArr[i]
        tMap.remove(gArr)
        lvl = self.convert(tMap, g)
        return lvl

    def convert(self, tMap, g):
        length = len(tMap)
        newMap = []
        for i in range(length):
            width = len(tMap[i])
            newMap.append([Tile([0, 0], 0, "None")] * width)
        for y in range(length):
            width = len(tMap[y])
            for x in range(width):
                pos = [x, y]
                str = tMap[y][x]
                if str == '+':
                    newMap[y][x] = Intersection(pos, 0, "None")
                    newMap[y][x].image = pg.transform.scale(pg.image.load("sprites\\tile_x_conveyor.png"),
                                                            (TILE_SIZE, TILE_SIZE))
                elif str in ["<", ">", "^", "v"]:
                    angle = 0 if str == '>' else (90 if str == '^' else (180 if str == '<' else 270))
                    newMap[y][x] = Belt(pos, angle, "None")
                elif str == 'X':
                    newMap[y][x] = Tile(pos, 0, "Out of Bounds")
                elif str == 'E':
                    newMap[y][x] = Exit(pos, 0, "None")
                elif str == 'I':
                    newMap[y][x] = Tile(pos, 0, "Iron Ore")
                elif str == 'W':
                    newMap[y][x] = Tile(pos, 0, "Wood")
                elif str == 'C':
                    newMap[y][x] = Tile(pos, 0, "Coal")
                elif str == 'O':
                    newMap[y][x] = Tile(pos, 0, "Oil")
                else:
                    newMap[y][x] = Tile(pos, 0, "None")
        return Level(newMap, g, self.lNum)


class Item:
    def __init__(self, name):
        self.name = name
        self.image = pg.image.load("sprites\\tile_grass.png")
        self.direction = pg.Vector2([0, 1])
        self.moved = True
        if os.path.exists("sprites\\" + name + ".png"):
            self.image = pg.image.load("sprites\\" + name + ".png")
        else:
            self.image = pg.image.load("sprites\\tile_grass.png")
        self.direction = pg.Vector2([0, 1])
        self.moved = True
        self.manufactured = False
        self.offset = 0


class Recipe:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

    def get_outputs(self):
        temp = []
        for i in self.outputs:
            temp.append(Item(i))
        return temp

    def check_inputs(self, inputs):
        for j in self.inputs:
            contained = False
            for i in inputs:
                if i.name == j and not i.manufactured:
                    contained = True
            if not contained:
                return False
        return True


class RecipeCollection:
    def __init__(self, recipes):
        self.recipes = []
        self.recipes.extend(recipes)

    def get_recipe(self, inputs):
        for r in self.recipes:
            if r.check_inputs(inputs):
                return r
        return False


class Tile:
    def __init__(self, pos, angle, resource, ghost=False):
        self.pos = pos
        self.direction = pg.Vector2([1, 0]).rotate(angle)
        self.resource = resource  # None, Iron, Wood, Coal, Oil, Out of Bounds
        if self.resource == "None":
            self.image = pg.transform.scale(pg.image.load("sprites\\tile_grass.png"), (TILE_SIZE, TILE_SIZE))
        elif self.resource == "Out of Bounds":
            self.image = pg.transform.scale(pg.image.load("sprites\\OOB.png"), (TILE_SIZE, TILE_SIZE))
        else:
            self.image = pg.transform.scale(pg.image.load("sprites\\tile_" + self.resource + ".png"),
                                            (TILE_SIZE, TILE_SIZE))
        if ghost:
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)
        self.image_rot = []
        self.type = "Tile"
        self.items = []

    def __str__(self):
        return str(self.type) + ": " + str(self.pos)

    def get_x(self):
        return (math.floor(SURF.get_width() / 2 + (self.pos[0] - len(level.tile_array[0]) / 2) * TILE_SIZE))

    def get_y(self):
        return (math.floor(SURF.get_height() / 2 + (self.pos[1] - len(level.tile_array) / 2) * TILE_SIZE))

    def blit(self, surf):
        if len(self.image_rot) == 0:
            self.image_rot = [pg.transform.rotate(self.image, 0), pg.transform.rotate(self.image, 270),
                              pg.transform.rotate(self.image, 180), pg.transform.rotate(self.image, 90)]
        surf.blit(self.image_rot[int((self.direction.angle_to(pg.Vector2([1, 0])) % 360) / 90)],
                  (self.pos[0] * TILE_SIZE, self.pos[1] * TILE_SIZE))

    def draw(self):
        if len(self.image_rot) == 0:
            self.image_rot = [pg.transform.rotate(self.image, 0), pg.transform.rotate(self.image, 270),
                              pg.transform.rotate(self.image, 180), pg.transform.rotate(self.image, 90)]
        SURF.blit(self.image_rot[int((self.direction.angle_to(pg.Vector2([1, 0])) % 360) / 90)],
                  (self.get_x(), self.get_y()))

    def tick(self):
        if self.type != "Tile":
            for i in self.items:
                i.offset += TICK_RATE / FPS
                if i.moved:
                    i.direction = self.direction
                    i.moved = False
            i = 0
            while i < len(self.items):
                if not self.items[i].moved and self.items[i].offset > 1 and \
                        -1 < int(self.pos[1] - self.items[i].direction.y) < len(level.tile_array) and -1 < int(
                        self.pos[0] + self.items[i].direction.x) < len(level.tile_array[0]):
                    temp = self.items.pop(i)
                    temp.moved = True
                    temp.manufactured = False
                    temp.offset -= 1
                    level.tile_array[int(self.pos[1] - temp.direction.y)][
                        int(self.pos[0] + temp.direction.x)].items.append(temp)
                elif self.items[i].offset > 2:
                    self.items.pop(i)
                else:
                    i += 1

    def is_open(self, type):
        if self.resource == "Out of Bounds":
            return False
        elif self.resource in ["Wood", "Oil", "Iron Ore", "Coal"] and type != "Extractor":
            return False
        elif self.resource not in ["Wood", "Oil", "Iron Ore", "Coal"] and type == "Extractor":
            return False
        elif self.type == "Exit":
            return False
        elif self.resource == "None" and type == "Extractor":
            return False
        return True


class Player:
    def __init__(self):
        self.selected_tile = "Tile"
        self.tile_angle = 0
        self.last_pos = [0, 0]
        self.ghost_tile = Tile(self.last_pos, 0, "None")

    def is_in_level(self):  # Detects if pos is within the level
        return self.get_x() < TILE_SIZE and self.get_y() < TILE_SIZE

    def can_place(self):  # should work
        return self.selected_tile and self.get_tile() and self.get_tile().is_open(self.selected_tile)

    def get_tile(self):  # works
        if -1 < self.get_y() < len(level.tile_array) and -1 < self.get_x() < len(level.tile_array[0]):
            return level.tile_array[self.get_y()][self.get_x()]
        return False

    def get_x(self):
        return (math.floor((self.last_pos[0] - SURF.get_width() / 2) / TILE_SIZE + len(level.tile_array[0]) / 2))

    def get_y(self):
        return (math.floor((self.last_pos[1] - SURF.get_height() / 2) / TILE_SIZE + len(level.tile_array) / 2))

    def place(self):  # works
        level.dirty = True
        level.tile_array[self.get_y()][self.get_x()] = sys.modules[
            __name__].__getattribute__(self.selected_tile)(
            [self.get_x(), (self.get_y())], self.tile_angle,
            level.tile_array[self.get_y()][self.get_x()].resource)

    def remove(self, pos):
        level.dirty = True
        self.last_pos = pos
        if self.get_tile() and level.tile_array[self.get_y()][self.get_x()].type != "Exit":
            level.tile_array[self.get_y()][self.get_x()] = Tile(
                [self.get_x(), self.get_y()], self.tile_angle,
                level.tile_array[self.get_y()][self.get_x()].resource)

    def click(self, pos):
        self.last_pos = pos
        if self.is_in_level():
            if self.can_place():
                self.place()

    def move(self, pos):
        self.last_pos = pos
        self.ghost_tile = sys.modules[__name__].__getattribute__(self.selected_tile)(
            [self.get_x(), self.get_y()], self.tile_angle, "None", True)

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
            self.selected_tile = "Void"
        elif key == pg.K_r:
            self.tile_angle = (self.tile_angle - 90) % 360


class Extractor(Tile):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Extractor"
        if self.resource in ["None", "Out of Bounds"]:
            self.image = pg.transform.scale(pg.image.load("sprites\\tile_forest.png"), (TILE_SIZE, TILE_SIZE))
        else:
            self.image = pg.transform.scale(pg.image.load("sprites\\tile_" + self.resource + ".png"),
                                            (TILE_SIZE, TILE_SIZE))
        if ghost:
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)
        self.dt = 0

    def tick(self):
        # adds an item based on resources
        super(Extractor, self).tick()
        self.dt += 1 / FPS * TICK_RATE
        if self.dt > 1 / TICK_RATE:
            self.items.append(Item(self.resource))
            self.dt -= 1 / TICK_RATE


class Manufacturer(Tile):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Manufacturer"
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_factory.png"), (TILE_SIZE, TILE_SIZE))
        self.dt = 0
        if ghost:
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)

    def tick(self):
        # if Recipie Collection class says that the items in self.items can be made into a recipie, consumes them and outputs the result
        self.dt += 1 / FPS * TICK_RATE
        if self.dt > 1 / TICK_RATE:
            if rc.get_recipe(self.items):
                recipe = rc.get_recipe(self.items)
                for i in recipe.inputs:
                    for index in range(len(self.items)):
                        if self.items[index].name == i:
                            self.items.pop(index)
                            break
                outputs = recipe.get_outputs()
                for item in outputs:
                    item.manufactured = True
                self.items.extend(outputs)
        for i in self.items:
            if i.manufactured:
                i.offset += TICK_RATE / FPS
            if i.moved:
                i.direction = self.direction
                i.moved = False
        i = 0
        while i < len(self.items):
            if not self.items[i].moved and self.items[i].offset > 1 and \
                    -1 < int(self.pos[1] - self.items[i].direction.y) < len(level.tile_array) and -1 < int(
                self.pos[0] + self.items[i].direction.x) < len(level.tile_array[0]):
                temp = self.items.pop(i)
                temp.moved = True
                temp.manufactured = False
                temp.offset -= 1
                level.tile_array[int(self.pos[1] - temp.direction.y)][int(self.pos[0] + temp.direction.x)].items.append(
                    temp)
            elif self.items[i].offset > 2:
                self.items.pop(i)
            else:
                i += 1


class Belt(Tile):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Belt"
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_conveyor.png"), (TILE_SIZE, TILE_SIZE))
        if ghost:
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)


class Intersection(Belt):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Intersection"
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_x_conveyor.png"), (TILE_SIZE, TILE_SIZE))
        if ghost:
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)

    def tick(self):
        for i in self.items:
            i.offset += TICK_RATE / FPS
            if i.moved:
                i.moved = False
        i = 0
        while i < len(self.items):
            if not self.items[i].moved and self.items[i].offset > 1 and \
                    -1 < int(self.pos[1] - self.items[i].direction.y) < len(level.tile_array) and -1 < int(
                self.pos[0] + self.items[i].direction.x) < len(level.tile_array[0]):
                temp = self.items.pop(i)
                temp.moved = True
                temp.manufactured = False
                temp.offset -= 1
                level.tile_array[int(self.pos[1] - temp.direction.y)][int(self.pos[0] + temp.direction.x)].items.append(
                    temp)
            elif self.items[i].offset > 2:
                self.items.pop(i)
            else:
                i += 1


class Splitter(Belt):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Splitter"
        self.split_bool = False  # False = right, True = left
        self.image = pg.transform.scale(pg.image.load("sprites\\Splitter.png"), (TILE_SIZE, TILE_SIZE))
        if ghost:
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)

    def tick(self):
        # Alternates between left and right
        for i in self.items:
            i.offset += TICK_RATE / FPS
            if i.moved:
                i.direction = self.direction.rotate(90 if self.split_bool else 270)
                self.split_bool = not self.split_bool
                i.moved = False
        i = 0
        while i < len(self.items):
            if not self.items[i].moved and self.items[i].offset > 1 and -1 < int(
                    self.pos[1] - self.items[i].direction.y) \
                    < len(level.tile_array) and -1 < int(self.pos[0] + self.items[i].direction.x) < len(
                level.tile_array[0]):
                temp = self.items.pop(i)
                temp.moved = True
                temp.manufactured = False
                temp.offset -= 1
                level.tile_array[int(self.pos[1] - temp.direction.y)][int(self.pos[0] + temp.direction.x)].items.append(
                    temp)
            elif self.items[i].offset > 2:
                self.items.pop(i)
            else:
                i += 1


class Void(Tile):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Void"
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_grass.png"), (TILE_SIZE, TILE_SIZE))
        if ghost:
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)

    def tick(self):
        self.items = []


class Exit(Tile):
    def __init__(self, pos, angle, resource):
        super().__init__(pos, angle, resource)
        self.image = pg.transform.scale(pg.image.load("sprites\\Alloy Plate.png"), (TILE_SIZE, TILE_SIZE))
        self.type = "Exit"
        self.dt = 0

    def tick(self):
        global level
        self.dt += 1 / FPS * TICK_RATE
        if self.dt > 10 / TICK_RATE:
            self.items.append(Item(self.resource))
            self.dt -= 10 / TICK_RATE
            temp_item_num = 0
            for i in self.items:
                if i.name == level.goal:
                    temp_item_num += 1
                elif i.name != "None":
                    self.items = []
                    temp_item_num = 0
                    print("REJECTED")
            if temp_item_num >= 10:
                print("done")
                level = level.next_level()
            self.items = []


rc = RecipeCollection((Recipe(["Wood", "Iron Ore"], ["Iron Bar"]), Recipe(["Natural Gas", "Iron Ore"], ["Iron Bar"]),
                       Recipe(["Coal", "Iron Bar"], ["Steel Bar"]), Recipe(["Iron Bar"], ["Iron Tubes"]),
                       Recipe(["Iron Tubes"], ["Screws"]),
                       Recipe(["Steel Bar"], ["Steel Tubes"]), Recipe(["Steel Bar", "Iron Bar"], ["Alloy Plate"]),
                       Recipe(["Steel Tubes"], ["Springs"]), Recipe(["Screws", "Springs"], ["Machine Parts"]),
                       Recipe(["Alloy Plate", "Machine Parts", "Steel Tubes"], ["Engines"]),
                       Recipe(["Engines", "Springs", "Coal"], ["Locomotives"]),
                       Recipe(["Engines", "Alloy Plate", "Gasoline"], ["Automobiles"]),
                       Recipe(["Steel Tubes", "Plastic"], ["Consumer Goods"]),
                       Recipe(["Oil"], ["Natural Gas", "Petroleum"]), Recipe(["Petroleum"], ["Plastic", "Gasoline"])))
load = Loader()
level = load.load_level(9)  # 0.txt is just a dummy for testing
player = Player()
t = time.perf_counter()
fps_arr = [1 / FPS] * 30
tutorial_cleared = False
tutorial_text = "[tutorial goes here, press enter to continue]"

while True:
    SURF.fill((0, 0, 0))
    if tutorial_cleared:
        level.world_tick()
        level.draw_level()
        player.ghost_tile.draw()
    else:
        f = pg.font.SysFont("Arial", 30)
        r = f.render(tutorial_text, True, pg.Color("white"))
        SURF.blit(r, [(SURF.get_width() - r.get_width()) / 2, (SURF.get_height() - r.get_height()) / 2])
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if not tutorial_cleared:
                if event.key == pg.K_RETURN:
                    tutorial_cleared = True
            else:
                player.select(event.key)
        elif event.type == pg.MOUSEBUTTONUP and tutorial_cleared:
            if event.button == pg.BUTTON_LEFT:
                player.click(event.pos)
            elif event.button == pg.BUTTON_RIGHT:
                player.remove(event.pos)
    f = pg.font.SysFont("Arial", 15)
    r = f.render(str(int(30 / sum(fps_arr))), True, pg.Color("white"))
    SURF.blit(r, (5, 5))
    if tutorial_cleared:
        player.move(pg.mouse.get_pos())
    pg.display.update()
    fps_arr.append(time.perf_counter() - t)
    t = time.perf_counter()
    fps_arr.pop(0)
    clock.tick(FPS)
