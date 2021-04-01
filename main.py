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
TILE_SIZE = 100  # dimensions of each tile in pixels
#####################


class Item:
    def __init__(self, name):
        self.name = name
        self.image = pg.image.load("New Piskel-1.png.png")
        self.direction = pg.Vector2([0, 0])
        self.moved = False


class Tile:
    def __init__(self, pos):
        self.pos = pos
        self.direction = pg.Vector2([0, 1])
        self.image = pg.transform.scale(pg.image.load("pacman.png"), (TILE_SIZE, TILE_SIZE))
        self.resource = "None"  # None, Iron, Wood, Coal, Oil, Out of Bounds
        self.type = "Tile"
        self.items = []

    def draw(self):
        SURF.blit(pg.transform.rotate(self.image, -self.direction.angle_to(pg.Vector2([1, 0]))), (self.pos[0] * TILE_SIZE, self.pos[1] * TILE_SIZE))

    def tick(self):
        # Every tile has the ability to move items
        for i in range(len(self.items)):
            if self.items[i].moved:
                continue
            temp = self.items.pop(i)
            i -= 1
            temp.direction = self.direction
            temp.moved = True
            level.tile_array[self.pos[0] + self.direction.x][self.pos[1] + self.direction.y].items.append(temp)

    def is_open(self, type):
        if self.resource == "Out of Bounds":
            return False
        elif self.resource is not None and type != "Extractor":
            return False
        return True


class Extractor(Tile):
    def __init__(self, pos):
        super().__init__(pos)
        self.type = "Extractor"

    def tick(self):
        # adds an item based on resources
        super(Extractor, self).tick()
        # TODO implement this


class Manufacturer(Tile):
    def __init__(self, pos):
        super().__init__(pos)
        self.type = "Manufacturer"

    def tick(self):
        # if Recipie Collection class says that the items in self.items can be made into a recipie, consumes them and outputs the result
        super(Manufacturer, self).tick()
        # TODO implement this


class Belt(Tile):
    def __init__(self, pos):
        super().__init__(pos)
        self.type = "Belt"

    def draw(self):
        super(Belt, self).draw()
        if len(self.items) > 0:
            img = pg.transform.scale(self.items[0].image, (int(TILE_SIZE / 2), int(TILE_SIZE / 2)))
            SURF.blit(img, (self.pos[0] * TILE_SIZE + TILE_SIZE / 4, self.pos[1] * TILE_SIZE + TILE_SIZE / 4))


class Intersection(Tile):
    def __init__(self, pos):
        super().__init__(pos)
        self.type = "Intersection"

    def tick(self):
        # Respects item direction
        for i in range(len(self.items)):
            if self.items[i].moved:
                continue
            temp = self.items.pop(i)
            i -= 1
            temp.moved = True
            level.tile_array[self.pos[0] + temp.direction.x][self.pos[1] + temp.direction.y].items.append(temp)


class Splitter(Tile):
    def __init__(self, pos):
        super().__init__(pos)
        self.type = "Splitter"
        self.split_bool = False  # False = right, True = left

    def tick(self):
        # Alternates between left and right
        for i in range(len(self.items)):
            if self.items[i].moved:
                continue
            self.split_bool = not self.split_bool
            temp = self.items.pop(i)
            i -= 1
            direction = pg.Vector2(self.direction[0], self.direction[1])
            temp.direction = direction.rotate(90 if self.split_bool else 270)
            temp.moved = True
            level.tile_array[self.pos[0] + temp.direction.x][self.pos[1] + temp.direction.y].items.append(temp)






level = None  # Level class, overwritten when the loader is called

while True:
    tile = Belt((1, 1))
    tile.direction = pg.Vector2([0, 1])
    tile.items.append(Item("Iron"))
    tile.draw()
    for event in pg.event.get():
        if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
    pg.display.update()
    clock.tick(FPS)