from itertools import repeat

from physics import PhysicsEngine
from settings import *
import moderngl as mgl
import pygame as pg
import sys
# from shader_program import ShaderProgram
from scene import Scene
from player import Player
from textures import Textures


def noop(*args, **kwargs):
    return


class NoOp:
    def __call__(self, *args, **kwargs):
        return NoOp()
    def __getitem__(self, item):
        return NoOp()
    def __getattr__(self, item):
        return NoOp()
    def __iter__(self):
        return repeat(NoOp(), 2)
    def __mul__(self, other):
        return other


class CTX:
    """Fake"""
    buffer = noop
    vertex_array = noop


class ShaderProgram:
    """Fake"""
    chunk = None
    water = None
    bedrock = None
    voxel_marker = None
    meshes = {}

    def __init__(self, app):
        self.app = app


class Clock:
    def __init__(self, delta_time=0.01):
        self.ticks = 0
        self.delta_time = delta_time

    def tick(self):
        if self.ticks > 10:
            sys.exit()
        self.ticks += 1
        return self.delta_time

    def get_ticks(self):
        return self.ticks

    def get_fps(self):
        return 1/self.delta_time


class TestEngine:
    def __init__(self):

        self.ctx = CTX()

        self.clock = Clock()
        self.delta_time = 0
        self.time = 0

        self.is_running = True
        self.on_init()

    def on_init(self):
        self.textures = None
        self.player = Player(self, pg=NoOp())
        self.shader_program = ShaderProgram(self)
        self.scene = Scene(self)
        self.physics = PhysicsEngine(self.scene.world)
        self.physics.register_movable(self.player)

    def update(self):
        self.delta_time = self.clock.tick()
        self.time = self.clock.get_ticks() * 0.001
        self.physics.update()
        self.scene.update()
        pg.display.set_caption(f'{self.clock.get_fps():5.0f} FPS '
                               f' player is_standing: {self.player.action_controller.is_standing}'
                               f' [{self.player.accel.y}]')

    def run(self):
        while self.is_running:
            self.update()
        sys.exit()


if __name__ == "__main__":
    app = TestEngine()
    app.run()
