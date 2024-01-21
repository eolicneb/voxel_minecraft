from settings import *


class ShaderProgram:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.camera = app.player.camera
        # ------- shaders ------- #
        self.chunk = self.get_program(shader_name='chunk')
        self.water = self.get_program(shader_name='water')
        self.bedrock = self.get_program(shader_name='bedrock')
        self.voxel_marker = self.get_program(shader_name='voxel_marker')
        # ----------------------- #
        self.set_uniforms_on_init()

    def set_uniforms_on_init(self):
        # chunk
        self.chunk['m_proj'].write(self.camera.m_proj)
        self.chunk['m_model'].write(glm.mat4())
        self.chunk['bg_color'].write(BG_COLOR)
        self.chunk['water_line'] = WATER_LINE
        self.chunk['u_texture_array_0'] = 1

        # bedrock
        self.bedrock['m_proj'].write(self.camera.m_proj)
        self.bedrock['bg_color'].write(BG_COLOR)
        self.bedrock['u_texture_array_0'] = 1

        # marker
        self.voxel_marker['m_proj'].write(self.camera.m_proj)
        self.voxel_marker['m_model'].write(glm.mat4())
        self.voxel_marker['u_texture_0'] = 0

        # water
        self.water['m_proj'].write(self.camera.m_proj)
        self.water['u_texture_2'] = 2
        self.water['bg_color'].write(BG_COLOR)

    def update(self):
        self.chunk['m_view'].write(self.camera.m_view)
        self.voxel_marker['m_view'].write(self.camera.m_view)
        self.water['m_view'].write(self.camera.m_view)
        self.bedrock['m_view'].write(self.camera.m_view)

    def get_program(self, shader_name):
        with open(f'shaders/{shader_name}.vert') as file:
            vertex_shader = file.read()

        with open(f'shaders/{shader_name}.frag') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program
