import math
import os
import sys
import time
import random

import pygame as pg

os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
clock = pg.time.Clock()
W = pg.display.Info().current_w
H = pg.display.Info().current_h
SURF = pg.display.set_mode((W, H), pg.NOFRAME)

#####CONSTANTS#####
FPS = 60
TICK_RATE = 1.5  # ticks per second

if SURF.get_width() / 20 > SURF.get_height() / 10:
    TILE_SIZE = SURF.get_height() // 10  # dimensions of each tile in pixels
else:
    TILE_SIZE = SURF.get_width() // 20
#####################
bufferSize = 9
transition_cd = 0

class Level:
    def __init__(self, tMap, g, n):
        self.number = n
        self.tile_array = tMap
        self.length = len(self.tile_array)
        self.width = len(self.tile_array[0])
        self.goal = g
        self.surf = pg.Surface([0, 0])
        self.dirty = True
        self.time = 0
        self.transition_cd = 0

    def world_tick(self):
        global tutorial_cleared
        done = False
        for tiley in range(self.length):
            for tilex in range(self.width):
                if self.tile_array[tiley][tilex].tick():
                    done = True
                    break
            if done:
                break
        if tutorial_cleared:
            self.time += sum(fps_arr) / 30

    def draw_level(self):
        global transition_cd
        if self.number == 0:
            SURF.fill((0, 0, 0))
            rc.show_recipes = False
            f = pg.font.SysFont("Comic Sans MS", 60, True)
            yw = f.render("The Overlord is satisfied. You live to see another day.", True, pg.Color("red"))
            fs = f.render("Final Score: " + str(score), True, pg.Color("red"))
            hs = f.render("High Score: " + str(hiScore), True, pg.Color("red"))
            SURF.blit(yw, [(SURF.get_width() - yw.get_width()) / 2, (SURF.get_height() - yw.get_height() - 150) / 2])
            SURF.blit(fs, [(SURF.get_width() - fs.get_width()) / 2, (SURF.get_height() - fs.get_height()) / 2])
            SURF.blit(hs, [(SURF.get_width() - hs.get_width()) / 2, (SURF.get_height() - hs.get_height() + 150) / 2])
        else:
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
            SURF.blit(self.surf,
                      [(SURF.get_width() - self.surf.get_width()) / 2,
                       (SURF.get_height() - self.surf.get_height()) / 2])
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
        global transition_cd
        if transition_cd > 0 and self.number != 10 and self.number != 0:
            f = pg.font.SysFont("Comic Sans MS", 60, True)
            r = f.render("YOUR OFFERING HAS BEEN ACCEPTED", True, pg.Color(255, 32, 32))
            SURF.blit(r, [(SURF.get_width() - r.get_width()) / 2, (SURF.get_height() - r.get_height()) / 2])
            transition_cd -= sum(fps_arr) / 30

    def next_level(self):
        global load, score, hiScore, transition_cd
        transition_cd = 3
        score += 10 * int(10000 * (self.number ** 2.75) / (self.time - (5 / TICK_RATE)))
        if self.number != 10:
            return load.load_level(self.number + 1)
        else:
            return load.load_level(0)


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
        for l in range(len(tMap)):
            for i in range(bufferSize):
                tMap[l].insert(0, "B")
                tMap[l].append("B")
        list = ["B"] * len(tMap[0])
        for i in range(bufferSize):
            tMap.insert(0, list)
            tMap.append(list)
        lvl = self.convert(tMap, g)
        return lvl

    def convert(self, tMap, g):
        length = len(tMap)
        newMap = []
        for i in range(length):
            width = len(tMap[i])
            newMap.append([Tile([0, 0], 0, "BG")] * width)
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
                elif str == 'B':
                    newMap[y][x] = Tile(pos, 0, "BG")
                elif str == 'n':
                    newMap[y][x] = Tile(pos, 0, "E")
                elif str == 'e':
                    newMap[y][x] = Tile(pos, 270, "E")
                elif str == 's':
                    newMap[y][x] = Tile(pos, 180, "E")
                elif str == 'w':
                    newMap[y][x] = Tile(pos, 90, "E")
                elif str == 'se':
                    newMap[y][x] = Tile(pos, 180, "C")
                elif str == 'ne':
                    newMap[y][x] = Tile(pos, 270, "C")
                elif str == 'nw':
                    newMap[y][x] = Tile(pos, 0, "C")
                elif str == 'sw':
                    newMap[y][x] = Tile(pos, 90, "C")
                else:
                    newMap[y][x] = Tile(pos, 0, "None")
        return Level(newMap, g, self.lNum)


class Item:
    def __init__(self, name):
        self.name = name
        self.image = pg.image.load("sprites\\tile_grass_" + str(random.randint(1, 3)) + ".png")
        self.direction = pg.Vector2([0, 1])
        self.moved = True
        if os.path.exists("sprites\\" + name + ".png"):
            self.image = pg.image.load("sprites\\" + name + ".png")
        else:
            self.image = pg.image.load("sprites\\tile_grass_" + str(random.randint(1, 3)) + ".png")
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

    def get_image(self):
        temp_surf = pg.Surface((int(TILE_SIZE * 3), TILE_SIZE / 2))
        temp_surf.fill((100, 100, 100))
        temp_surf.blit(pg.transform.smoothscale(pg.image.load("sprites\\arrow.png"), (TILE_SIZE // 3, TILE_SIZE // 3)),
                       ((TILE_SIZE * 3) // 2 + TILE_SIZE // 12, TILE_SIZE // 12))
        for i in range(len(self.outputs)):
            pg.draw.rect(temp_surf, (125, 125, 125), ((i + 4) * TILE_SIZE //
                2 + TILE_SIZE // 24 - 1, TILE_SIZE // 24 - 1, 5 * TILE_SIZE // 12, 5 * TILE_SIZE // 12))
            pg.draw.rect(temp_surf, (150, 150, 150), ((i + 4) * TILE_SIZE //
                2 + TILE_SIZE // 24 + 1, TILE_SIZE // 24 + 1, 5 * TILE_SIZE // 12, 5 * TILE_SIZE // 12))
            temp_surf.blit(pg.transform.smoothscale(pg.image.load("sprites\\" + self.outputs[i] + ".png"),
                                                    (TILE_SIZE // 3, TILE_SIZE // 3)),
                           ((i + 4) * TILE_SIZE // 2 + TILE_SIZE // 12, TILE_SIZE // 12))
        for i in range(len(self.inputs)):
            pg.draw.rect(temp_surf, (125, 125, 125), (
                (2 - i) * TILE_SIZE // 2 + TILE_SIZE // 24 - 1, TILE_SIZE // 24 - 1, 5 * TILE_SIZE // 12,
                5 * TILE_SIZE // 12))
            pg.draw.rect(temp_surf, (150, 150, 150), (
                (2 - i) * TILE_SIZE // 2 + TILE_SIZE // 24 + 1, TILE_SIZE // 24 + 1, 5 * TILE_SIZE // 12,
                5 * TILE_SIZE // 12))
            temp_surf.blit(pg.transform.smoothscale(pg.image.load("sprites\\" + self.inputs[i] + ".png"),
                                                    (TILE_SIZE // 3, TILE_SIZE // 3)),
                           ((2 - i) * TILE_SIZE // 2 + TILE_SIZE // 12, TILE_SIZE // 12))
        return temp_surf


class RecipeCollection:
    def __init__(self, recipes):
        self.recipes = []
        self.recipes.extend(recipes)
        self.image = self.get_image()
        self.show_recipes = True

    def get_recipe(self, inputs):
        for r in self.recipes:
            if r.check_inputs(inputs):
                return r
        return False

    def get_image(self):
        temp_surf = pg.Surface((int(TILE_SIZE * 3.25), (TILE_SIZE // 2) * len(self.recipes) + TILE_SIZE // 4))
        temp_surf.fill((50, 50, 50))
        for i in range(len(self.recipes)):
            temp_surf.blit(self.recipes[i].get_image(), (TILE_SIZE // 8, i * TILE_SIZE // 2 + TILE_SIZE // 8))
        return temp_surf


class Tile:
    def __init__(self, pos, angle, resource, ghost=False):
        self.pos = pos
        self.direction = pg.Vector2([1, 0]).rotate(angle)
        self.resource = resource  # None, Iron, Wood, Coal, Oil, Out of Bounds
        if self.resource == "None":
            self.image = pg.transform.scale(
                pg.image.load("sprites\\tile_grass_" + (str(random.randint(1, 3)) if not ghost else "1") + ".png"),
                (TILE_SIZE, TILE_SIZE))
        elif self.resource == "Out of Bounds":
            self.image = pg.transform.scale(pg.image.load("sprites\\OOB.png"), (TILE_SIZE, TILE_SIZE))
        elif self.resource == "BG":
            self.image = pg.transform.scale(pg.image.load("sprites\\tile_Ocean.png"), (TILE_SIZE, TILE_SIZE))
        elif self.resource == "E":
            self.image = pg.transform.rotate(pg.transform.scale(pg.image.load("sprites\\tile_Ocean.png"), (TILE_SIZE, TILE_SIZE)), -angle)
            self.image.blit(pg.transform.scale(pg.image.load("sprites\\tile_Border Flat.png"), (TILE_SIZE, TILE_SIZE)), (0, 0))
        elif self.resource == "C":
            self.image = pg.transform.rotate(pg.transform.scale(pg.image.load("sprites\\tile_Ocean.png"), (TILE_SIZE, TILE_SIZE)), -angle)
            self.image.blit(pg.transform.scale(pg.image.load("sprites\\tile_Border Corner.png"), (TILE_SIZE, TILE_SIZE)), (0, 0))
        else:
            self.image = pg.transform.scale(
                pg.image.load("sprites\\tile_grass_" + (str(random.randint(1, 3)) if not ghost else "1") + ".png"),
                (TILE_SIZE, TILE_SIZE))
            self.image.blit(pg.transform.scale(pg.image.load("sprites\\tile_" + self.resource + ".png"),
                                            (TILE_SIZE, TILE_SIZE)), (0, 0))
        if ghost:
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)
        self.image_rot = []
        self.type = "Tile"
        self.items = []

    def __str__(self):
        return str(self.type) + ": " + str(self.pos)

    def get_x(self):
        return math.floor(SURF.get_width() / 2 + (self.pos[0] - len(level.tile_array[0]) / 2) * TILE_SIZE)

    def get_y(self):
        return math.floor(SURF.get_height() / 2 + (self.pos[1] - len(level.tile_array) / 2) * TILE_SIZE)

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
                i.offset += dt * TICK_RATE
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
        if len(self.items) > 20:
            self.items = [self.items[0]]

    def is_open(self, type):
        if self.resource in ["Out of Bounds", "BG", "E", "C"]:
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
        self.selected_tile = "Extractor"
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
        return math.floor((self.last_pos[0] - SURF.get_width() / 2) / TILE_SIZE + len(level.tile_array[0]) / 2)

    def get_y(self):
        return math.floor((self.last_pos[1] - SURF.get_height() / 2) / TILE_SIZE + len(level.tile_array) / 2)

    def place(self):  # works
        level.dirty = True
        level.tile_array[self.get_y()][self.get_x()] = sys.modules[
            __name__].__getattribute__(self.selected_tile)(
            [self.get_x(), (self.get_y())], self.tile_angle,
            level.tile_array[self.get_y()][self.get_x()].resource)

    def remove(self, pos):
        if self.get_tile() and level.tile_array[self.get_y()][self.get_x()].resource not in ["E", "C", "BG"]:
            level.dirty = True
            self.last_pos = pos
            if level.tile_array[self.get_y()][self.get_x()].type != "Exit":
                level.tile_array[self.get_y()][self.get_x()] = Tile(
                    [self.get_x(), self.get_y()], 0,
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
            self.image = pg.transform.scale(pg.image.load("sprites\\tile_Extractor.png"), (TILE_SIZE, TILE_SIZE))
        else:
            self.image = pg.transform.scale(
                pg.image.load("sprites\\tile_grass_" + (str(random.randint(1, 3)) if not ghost else "1") + ".png"),
                (TILE_SIZE, TILE_SIZE))
            self.image.blit(pg.transform.scale(pg.image.load("sprites\\tile_" + self.resource + " Extractor.png"),
                                               (TILE_SIZE, TILE_SIZE)), (0, 0))
        if ghost:
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)
        self.dt = 0

    def tick(self):
        # adds an item based on resources
        super(Extractor, self).tick()
        global dt
        self.dt += dt
        if self.dt > 1 / TICK_RATE:
            self.items.append(Item(self.resource))
            self.dt -= 1 / TICK_RATE


class Manufacturer(Tile):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Manufacturer"
        self.dt = 0
        if not ghost:
            self.image = pg.transform.scale(
                pg.image.load("sprites\\tile_grass_" + (str(random.randint(1, 3)) if not ghost else "1") + ".png"),
                (TILE_SIZE, TILE_SIZE))
            self.image.blit(pg.transform.scale(pg.image.load("sprites\\tile_factory.png"), (TILE_SIZE, TILE_SIZE)), (0, 0))
        else:
            self.image = pg.transform.scale(pg.image.load("sprites\\tile_factory.png"), (TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)

    def tick(self):
        # if Recipie Collection class says that the items in self.items can be made into a recipie, consumes them and outputs the result
        global dt
        self.dt += dt
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
                self.dt -= 1 / TICK_RATE
        for i in self.items:
            if i.manufactured:
                i.offset += dt * TICK_RATE
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
        if len(self.items) > 20:
            self.items = [self.items[0]]


class Belt(Tile):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Belt"
        if not ghost:
            self.image = pg.transform.scale(
                pg.image.load("sprites\\tile_grass_" + (str(random.randint(1, 3)) if not ghost else "1") + ".png"),
                (TILE_SIZE, TILE_SIZE))
            self.image.blit(pg.transform.scale(pg.image.load("sprites\\tile_conveyor.png"), (TILE_SIZE, TILE_SIZE)), (0, 0))
        else:
            self.image = pg.transform.scale(pg.image.load("sprites\\tile_conveyor.png"), (TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)


class Intersection(Belt):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Intersection"
        if not ghost:
            self.image = pg.transform.scale(
                pg.image.load("sprites\\tile_grass_" + (str(random.randint(1, 3)) if not ghost else "1") + ".png"),
                (TILE_SIZE, TILE_SIZE))
            self.image.blit(pg.transform.scale(pg.image.load("sprites\\tile_x_conveyor.png"), (TILE_SIZE, TILE_SIZE)), (0, 0))
        else:
            self.image = pg.transform.scale(pg.image.load("sprites\\tile_x_conveyor.png"), (TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)

    def tick(self):
        for i in self.items:
            i.offset += dt * TICK_RATE
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
        if len(self.items) > 20:
            self.items = [self.items[0]]


class Splitter(Belt):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Splitter"
        self.split_bool = False  # False = right, True = left
        if not ghost:
            self.image = pg.transform.scale(
                pg.image.load("sprites\\tile_grass_" + (str(random.randint(1, 3)) if not ghost else "1") + ".png"),
                (TILE_SIZE, TILE_SIZE))
            self.image.blit(pg.transform.scale(pg.image.load("sprites\\Splitter.png"), (TILE_SIZE, TILE_SIZE)), (0, 0))
        if ghost:
            self.image = pg.transform.scale(pg.image.load("sprites\\Splitter.png"), (TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)

    def tick(self):
        # Alternates between left and right
        for i in self.items:
            i.offset += dt * TICK_RATE
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
        if len(self.items) > 20:
            self.items = [self.items[0]]


class Void(Tile):
    def __init__(self, pos, angle, resource, ghost=False):
        super().__init__(pos, angle, resource, ghost)
        self.type = "Void"
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_Void.png"), (TILE_SIZE, TILE_SIZE))
        if ghost:
            self.image.fill((255, 255, 255, 125), None, pg.BLEND_RGBA_MULT)

    def tick(self):
        self.items = []


class Exit(Tile):
    def __init__(self, pos, angle, resource):
        super().__init__(pos, angle, resource)
        self.image = pg.transform.scale(pg.image.load("sprites\\tile_exit.png"), (TILE_SIZE, TILE_SIZE))
        self.type = "Exit"
        self.dt = 0

    def tick(self):
        global level, dt
        self.dt += dt
        if self.dt > 5 / TICK_RATE:
            self.items.append(Item(self.resource))
            self.dt -= 5 / TICK_RATE
            temp_item_num = 0
            for i in self.items:
                if i.name == level.goal:
                    temp_item_num += 1
                elif i.name != "None":
                    self.items = []
                    temp_item_num = 0
                    print("REJECTED")
            if temp_item_num >= 5:
                print("done")
                level = level.next_level()
                self.items = []
                return True
            self.items = []


def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pg.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text


rc = RecipeCollection((Recipe(["Alloy Plate", "Machine Parts", "Steel Tubes"], ["Engines"]),
                       Recipe(["Engines", "Alloy Plate", "Gasoline"], ["Automobiles"]),
                       Recipe(["Engines", "Springs", "Coal"], ["Locomotives"]),
                       Recipe(["Wood", "Iron Ore"], ["Iron Bar"]), Recipe(["Natural Gas", "Iron Ore"], ["Iron Bar"]),
                       Recipe(["Coal", "Iron Bar"], ["Steel Bar"]), Recipe(["Steel Bar", "Iron Bar"], ["Alloy Plate"]),
                       Recipe(["Screws", "Springs"], ["Machine Parts"]),
                       Recipe(["Steel Tubes", "Plastic"], ["Consumer Goods"]),
                       Recipe(["Oil"], ["Natural Gas", "Petroleum"]), Recipe(["Petroleum"], ["Plastic", "Gasoline"]),
                       Recipe(["Iron Bar"], ["Iron Tubes"]),
                       Recipe(["Iron Tubes"], ["Screws"]),
                       Recipe(["Steel Bar"], ["Steel Tubes"]),
                       Recipe(["Steel Tubes"], ["Springs"])))
load = Loader()
level = load.load_level(9)
player = Player()
t = time.perf_counter()
dt = 0
fps_arr = [1 / FPS] * 30
tutorial_cleared = False
tutorial_text = "The Overlord requires a tribute of industrial parts and machinery. To construct this machinery, you must extract resources and combine them into more developed goods, using extractors and manufacturers respectively. You can select these, as well as other important tiles, using the number pad. Left click to drop tiles, right click to delete them, and push r to rotate. Extractors act as belts, you cannot build on rocks, and The Overlord requires a constant influx of the target item to be satisfied. You can see the target item on the corner of The Overlord, and the recipes to manufacture items can be toggled with the tab key. The Overlord will give you a score based on the speed of your completion following each of the 10 levels. At any time, you may surrender to The Overlord with the escape key, or reset your level with the backspace button. Push any key to go to that level, or enter to start from the beginning."
score = 0
hiScore = 0
while True:
    if score > int(open("highscore.txt").read()):
        hiScore = score
    else:
        hiScore = int(open("highscore.txt").read())
    SURF.fill((0, 0, 0))
    if tutorial_cleared:
        level.world_tick()
        level.draw_level()
        player.ghost_tile.draw()
        if rc.show_recipes:
            SURF.blit(rc.image, (0, (SURF.get_height() - rc.image.get_height()) // 2))
            img = pg.image.load("sprites\\hotbar.png")
            SURF.blit(pg.transform.smoothscale(img, (int(W / 3), int(img.get_height() * W / (3 * img.get_width())))),
                      (W / 3, H - (int(img.get_height() * W / (3 * img.get_width())))))
    else:
        f = pg.font.SysFont("Arial", 30)
        drawText(SURF, tutorial_text, pg.Color("white"), (TILE_SIZE, TILE_SIZE, SURF.get_width()-2*TILE_SIZE, SURF.get_height()-2*TILE_SIZE), f, True)
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            if score > int(open("highscore.txt").read()):
                hsFile = open("highscore.txt", "w")
                hsFile.write(str(int(score)))
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            numKeys = [pg.K_RETURN, pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9, pg.K_0]
            if not tutorial_cleared:
                if event.key in numKeys:
                    lvlNum = numKeys.index(event.key)
                    if lvlNum == 0:
                        level = load.load_level(1)
                    else:
                        print(lvlNum)
                        level = load.load_level(lvlNum)
                        print(level.number)
                    tutorial_cleared = True
            else:
                if event.key == pg.K_TAB:
                    rc.show_recipes = not rc.show_recipes
                elif event.key == pg.K_BACKSPACE:
                    level = load.load_level(level.number)
                else:
                    player.select(event.key)
        elif event.type == pg.MOUSEBUTTONUP and tutorial_cleared:
            if event.button == pg.BUTTON_LEFT:
                player.click(event.pos)
            elif event.button == pg.BUTTON_RIGHT:
                player.remove(event.pos)
    f = pg.font.SysFont("Arial", 15)
    s = pg.font.SysFont("Arial Bold", 50)
    r = f.render(str(int(30 / sum(fps_arr))), True, pg.Color("white"))
    SURF.blit(r, (5, 5))
    if level.number != 0 and tutorial_cleared:
        tm = s.render("Time: " + str(int(level.time)) + "   ", True, pg.Color("white"))
        sc = s.render("   Score: " + str(int(score)) + "   ", True, pg.Color("white"))
        hs = s.render("   High Score: " + str(int(hiScore)), True, pg.Color("white"))
        ww = tm.get_width() + sc.get_width() + hs.get_width() + 20
        scoreSurf = pg.Surface((ww, tm.get_height() + 10))
        scoreSurf.fill((0, 67, 156))
        scoreSurf.blit(tm, ((scoreSurf.get_width() - (tm.get_width() + sc.get_width() + hs.get_width())) / 2, 5))
        scoreSurf.blit(sc, (
        (scoreSurf.get_width() - (tm.get_width() + sc.get_width() + hs.get_width())) / 2 + tm.get_width(), 5))
        scoreSurf.blit(hs, ((scoreSurf.get_width() - (
                    tm.get_width() + sc.get_width() + hs.get_width())) / 2 + tm.get_width() + sc.get_width(), 5))
        scoreSurf.set_alpha(150)
        SURF.blit(scoreSurf, ((W - ww) / 2, (TILE_SIZE - tm.get_height()) / 2))
    if tutorial_cleared:
        player.move(pg.mouse.get_pos())
    pg.display.update()
    dt = time.perf_counter() - t
    fps_arr.append(dt)
    t = time.perf_counter()
    fps_arr.pop(0)
    clock.tick(FPS)
