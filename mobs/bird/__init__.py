from copy import copy
from enum import Enum
from functools import cached_property
from uuid import uuid4

import pygame as pg

from action_controller import ActionController
from meshes.base_mesh import BaseMesh
from meshes.utils import *
from mobile import Movable, Mobile
from mobs.base import Mob
from settings import *
from events import *

import random


class Bird(Mob):
    max_count = WORLD_AREA
    count = 0

    def __init__(self, app, identifier=None, position=None, velocity=None, accel=None):
        self.identifier = identifier or f"{self.__class__.__name__}-{uuid4().hex[-12:]}"
        self.app = app

        self.size = 7.0
        self.soul = BirdSoul(self)
        self.movable = BirdMovable(self, position, velocity, accel)
        self.mesh = BirdMesh(self)

        self.birth_date = copy(self.app.time)

    @classmethod
    def spawn(cls, app):
        if cls.max_count and cls.max_count <= cls.count:
            return
        if random.random() < .01 * app.delta_time:
            pos = random.randint(0, CHUNK_SIZE*WORLD_D), CHUNK_SIZE*WORLD_H, random.randint(0, CHUNK_SIZE*WORLD_W), random.randint(1, 360)
            bird = Bird(app, position=Mobile(pos[:3], pos[-1] * 3.14/180, 0))
            cls.count += 1
            return bird

    def on_init(self):
        self.soul.on_init()
        self.mesh.on_init()
        self.is_alive = True

    def on_delete(self):
        self.__class__.count -= 1

    def handle_event(self, event):
        if not self.is_alive:
            return
        self.soul.handle_event(event)
        self.movable.handle_event(event)

    def update(self):
        if not self.is_alive:
            return
        self.soul.update()
        self.mesh.update()

    def render(self):
        if not self.is_alive:
            return
        if self.app.player.camera.frustum.point_is_on_frustum(self.movable.position.location, self.size):
            self.mesh.render()

    def render_see_through(self):
        if not self.is_alive:
            return
        self.mesh.render_see_through()

    @property
    def age(self):
        return self.app.time - self.birth_date

    def die(self):
        if not self.is_alive:
            return
        self.is_alive = False
        self.app.publish_event(MobDied(self))


class BirdSoul:
    def __init__(self, mob):
        self.mob = mob

    class States(Enum):
        soaring = 0
        flapping = 1
        turning_left = 2
        turning_right = 3

    def on_init(self):
        pass

    def handle_event(self, event):
        pass

    def update(self):
        if self.mob.age > 10:
            self.die()
        self.mob.movable.speed_forward(PLAYER_SPEED * glm.vec3(10, 0, 0))
        self.mob.movable.position.yaw += self.mob.app.delta_time * 0.0005
        self.mob.movable.position.pitch = glm.sin(self.mob.app.time*2) * .03

    def spawn(self):
        pass

    def act(self):
        pass

    def die(self):
        self.mob.die()


class BirdMesh(BaseMesh):
    image_file = "mobs/bird/bird.png"
    is_tex_array = False

    vertex_shader = """
#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_tex_coord;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec2 uv;

void main() {
    uv = in_tex_coord;
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}
    """
    fragment_shader = """
#version 330 core

layout (location = 0) out vec4 fragColor;

const vec3 gamma = vec3(2.2);
const vec3 inv_gamma = 1 / gamma;

in vec2 uv;

uniform sampler2D u_texture_0;
uniform vec3 bg_color;

void main() {
    vec3 tex_col = texture(u_texture_0, uv).rgb;
    tex_col = pow(tex_col, gamma);
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    tex_col = mix(tex_col, bg_color, (1.0 - exp2(-0.000015 * fog_dist * fog_dist)));
    tex_col = pow(tex_col, inv_gamma);
    fragColor = vec4(tex_col, 1.0);
}
"""

    def __init__(self, mob):
        self.name = mob.__class__.__name__.lower()
        super().__init__()
        self.mob = mob

        self.app = mob.app
        self.ctx = mob.app.ctx
        self.program = self.register_in_shader()

        self.vbo_format = '3f 2f'
        self.attrs = ('in_position', 'in_tex_coord')

        self.update_vao()

    def on_init(self):
        self.update_vao()

    def get_vertex_data(self):
        p = self.mob.size
        body = [
            # (0.5, 0.0, 0.0), (-.2, 0.0, 0.0), (0.0, 0.1, .05),
            # (0.0, .01, 0.0), (-.5, .01, 0.0), (-.45, 0.1, 0.2)
        ]
        wing = [
            (-.1, .05, 0.0), (0.1, .05, 0.0), (0.0, 0.1, 1.0)
        ]
        vertices = [*body, *wing]
        # vertices = [self._rotate(point) for point in vertices]
        vertices = [tuple(p * point for point in triangs) for triangs in vertices]
        vertices += list(reflex(vertices, (0, 0, 1)))
        vertices += list(invert_triangles(*vertices))

        body_uv = [
            # (.5, 0), (.5, .8), (.6, .3),
            # (.5, .5), (.5, 1), (.7, 1)
        ]
        wing_uv = [
            (1., .35), (.6, .35), (1., 1)
        ]
        uv = [*body_uv, *wing_uv]
        uv += list(reflex(uv, (1, 0), (.5, .5)))
        uv += list(invert_triangles(*uv))

        vertex_data = np.hstack([vertices, uv], dtype='float32')
        return vertex_data

    def set_uniform(self):
        self.program['m_model'].write(self.mob.movable.position.get_model_matrix())

    def render(self):
        self.set_uniform()
        super().render()

    def register_in_shader(self):
        return self.app.shader_program.subscribe_mesh(
            self.name,
            texture=self.is_tex_array or self.texture or None,
            texture_array=self.is_tex_array and self.texture or None,
            vertex_shader=self.vertex_shader,
            fragment_shader=self.fragment_shader,
            uniforms_callback=None
        )

    @cached_property
    def texture(self):
        return self.__load_texture()

    def __load_texture(self):
        return self.mob.app.textures.load_texture(
            texture_name=self.name,
            image=self.load_image(),
            file_name=self.image_file or self.name,
            is_tex_array=self.is_tex_array
        )

    def load_image(self):
        if not self.image_file:
            return
        return pg.image.load(self.image_file)

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render_see_through(self):
        pass


class BirdMovable(Movable):
    def __init__(self, mob, position=None, velocity=None, accel=None):
        super().__init__(position, velocity, accel)
        self.mob = mob

        self.action_controller = ActionController(self)
        self.action_controller.is_flying = True

    def handle_event(self, event):
        pass
