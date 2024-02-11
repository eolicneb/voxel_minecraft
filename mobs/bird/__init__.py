from copy import copy
from functools import cached_property
from uuid import uuid4

import pygame as pg

from action_controller import ActionController
from meshes.base_mesh import BaseMesh
from meshes.utils import *
from mobile import Movable
from settings import *


class Bird:
    def __init__(self, app, identifier=None, position=None, velocity=None, accel=None):
        self.identifier = identifier or f"{self.__class__.__name__}-{uuid4().hex[-12:]}"
        self.app = app
        self.soul = BirdSoul(self)
        self.mesh = BirdMesh(self)
        self.movable = BirdMovable(self, position, velocity, accel)

    def on_init(self):
        self.soul.on_init()
        self.mesh.on_init()

    def handle_event(self, event):
        self.soul.handle_event(event)
        self.movable.handle_event(event)

    def update(self):
        self.soul.update()
        self.mesh.update()

    def render(self):
        if self.app.player.camera.frustum.point_is_on_frustum(self.movable.position.location, 1.0):
            self.mesh.render()

    def render_see_through(self):
        self.mesh.render_see_through()


class BirdSoul:
    def __init__(self, mob):
        self.mob = mob
        self.folks = {}

    def on_init(self):
        pass

    def handle_event(self, event):
        pass

    def update(self):
        # self.mob.movable.speed_forward(PLAYER_SPEED * glm.vec3(1, 0, 0))
        # self.mob.movable.position.location.y = CHUNK_SIZE * 2
        # self.mob.movable.position.pitch += 0.1
        # self.mob.movable.position.yaw += 0.1
        # self.mob.movable.update()
        # print(self.mob.movable.position)
        self.mob.movable.position.location = glm.vec3(10, 5, 10)
        self.mob.movable.position.location.y += 10

    def spawn(self):
        pass

    def act(self):
        pass

    def die(self):
        pass


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
        p = 10
        body = [
            (0.5, 0.0, 0.0), (-.2, 0.0, 0.0), (0.0, 0.1, .05),
            (0.0, .01, 0.0), (-.5, .01, 0.0), (-.45, 0.1, 0.2)
        ]
        wing = [
            (0.1, .05, 0.0), (-.1, .05, 0.0), (0.0, 0.1, 1.0)
        ]
        vertices = [*body, *wing]
        vertices += list(reflex(vertices, (0, 0, 1)))
        vertices += list(invert_triangles(*vertices))
        vertices = [tuple(p * c for c in verts) for verts in vertices]

        body_uv = [
            (.5, 0), (.5, .8), (.6, .3),
            (.5, .5), (.5, 1), (.7, 1)
        ]
        wing_uv = [
            (1., .3), (.6, .3), (1., 1)
        ]
        uv = [*body_uv, *wing_uv]
        uv += list(reflex(uv, (1, 0), (.5, .5)))
        uv += list(invert_triangles(*uv))

        vertex_data = np.hstack([vertices, uv], dtype='float32')
        return vertex_data

    def get_model_matrix(self):
        m_model = glm.translate(glm.mat4(), self.mob.movable.position.location)
        m_model = self.mob.movable.position._rot * m_model
        return m_model

    def set_uniform(self):
        self.program['m_model'].write(self.get_model_matrix())

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
