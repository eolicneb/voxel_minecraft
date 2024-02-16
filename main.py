from collections import deque

from events import Event
from mobile import Mobile
from mobs.bird import Bird
from mobs.spawner import MobSpawner
from physics import PhysicsEngine
from settings import *
import moderngl as mgl
import pygame as pg
import sys
from shader_program import ShaderProgram
from scene import Scene
from player import Player
from textures import Textures


class VoxelEngine:
    def __init__(self):
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, 24)

        pg.display.set_mode(WIN_RES, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
        self.ctx.gc_mode = 'auto'

        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.time = 0

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

        self.events_queue = deque()

        self.is_running = True
        self.on_init()

    def on_init(self):
        self.textures = Textures(self)
        self.player = Player(self)
        self.shader_program = ShaderProgram(self)
        # self.bird = Bird(self)
        self.scene = Scene(self)
        self.physics = PhysicsEngine(self.scene.world)
        self.spawner = MobSpawner(self)
        self.spawner.register_mob_seed("bird")

        self.physics.register_movable(self.player)
        # self.scene.register_mob(self.bird.identifier, self.bird)
        # self.physics.register_movable(self.bird.movable)

    def update(self):
        self.delta_time = self.clock.tick()

        self.physics.update()
        self.player.camera.update()
        self.spawner.update()
        self.scene.update()
        self.shader_program.update()

        self.time = pg.time.get_ticks() * 0.001
        pg.display.set_caption(f'{self.clock.get_fps():5.0f} FPS '
                               f' [events {len(self.events_queue)}]'
                               f' [Mobs: {len(self.spawner.mobs)}')

    def render(self):
        self.ctx.clear(color=BG_COLOR)
        self.scene.render()
        pg.display.flip()

    def publish_event(self, event: Event):
        self.events_queue.append(event)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.is_running = False
            self.physics.handle_event(event=event)
        for event in self.events_queue:
            self.player.handle_event(event)
            self.spawner.handle_event(event)
            self.scene.handle_event(event)
            self.physics.handle_event(event)
        self.events_queue.clear()

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()
        pg.quit()
        sys.exit()


if __name__ == "__main__":
    app = VoxelEngine()
    app.run()
