from settings import *


class Physics:
    def __init__(self, world, water_line, movables: list = None):
        self.world = world
        self.water_line = water_line
        self.movables = movables or []

    def update(self):
        for movable in self.movables:
            pass
