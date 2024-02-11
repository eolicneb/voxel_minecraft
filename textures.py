from copy import copy

import pygame as pg
import moderngl as mgl


class Textures:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx

        # load texture
        self.texture_0 = self.load(file_name='frame.png')
        self.texture_2 = self.load(file_name='water.png')
        self.texture_array_0 = self.load(file_name='tex_array_0.png', is_tex_array=True)
        self.texture_3 = self.load(file_name='test.png')

        # assign texture unit
        self.texture_0.use(location=0)
        self.texture_array_0.use(location=1)
        self.texture_2.use(location=2)
        self.texture_3.use(location=3)

        self.textures = {
            0: self.texture_0,
            1: self.texture_array_0,
            2: self.texture_2,
        }
        self.texture_index = {
            'frame': 0,
            'tex_array_0': 1,
            'water': 2
        }
        self.__last_index = 2

    def load_texture(self, texture_name, image=None, file_name=None, is_tex_array=False):
        if texture_name in self.textures:
            return self.texture_index[texture_name]

        self.__last_index += 1
        index = copy(self.__last_index)
        self.textures[index] = self.textures[texture_name] = self.load(image, file_name or texture_name, is_tex_array)
        self.texture_index[texture_name] = index
        self.textures[index].use(location=index)
        return index

    def load(self, image=None, file_name=None, is_tex_array=False):
        assert image or file_name
        texture = image or pg.image.load(f'assets/{file_name}')
        texture = pg.transform.flip(texture, flip_x=True, flip_y=False)

        if is_tex_array:
            num_layers = 3 * texture.get_height() // texture.get_width()  # textures per layer
            texture = self.app.ctx.texture_array(
                size=(texture.get_width(), texture.get_height() // num_layers, num_layers),
                components=4,
                data=pg.image.tostring(texture, 'RGBA')
            )
        else:
            texture = self.ctx.texture(
                size=texture.get_size(),
                components=4,
                data=pg.image.tostring(texture, 'RGBA', False)
            )
        texture.anisotropy = 32.0
        texture.build_mipmaps()
        texture.filter = (mgl.NEAREST, mgl.NEAREST)
        return texture
