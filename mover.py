from functools import cached_property

from settings import *


class BoundingBox:
    __ftr = glm.vec3( 1,  1,  1) / 2  # front-top-right
    __ftl = glm.vec3( 1,  1, -1) / 2  # front-top-left
    __fbl = glm.vec3( 1, -1, -1) / 2  # front-bottom-left
    __fbr = glm.vec3( 1, -1,  1) / 2  # front-bottom-right
    __btr = glm.vec3(-1,  1,  1) / 2  # back-top-right
    __btl = glm.vec3(-1,  1, -1) / 2  # back-top-left
    __bbl = glm.vec3(-1, -1, -1) / 2  # back-bottom-left
    __bbr = glm.vec3(-1, -1,  1) / 2  # back-bottom-right

    __box_offsets = [__ftr, __ftl, __fbl, __fbr,
                     __btr, __btl, __bbl, __bbr]
    __front_offsets  = [__ftr, __ftl, __fbl, __fbr]
    __back_offsets   = [__btr, __bbr, __bbl, __btl]
    __top_offsets    = [__ftr, __btr, __btl, __ftl]
    __bottom_offsets = [__fbr, __fbl, __bbl, __bbr]
    __right_offsets  = [__ftr, __fbr, __bbr, __btr]
    __left_offsets   = [__ftl, __btl, __bbl, __fbl]

    def __init__(self, depth, height, width):
        self.x = self.depth = depth
        self.y = self.height = height
        self.z = self.width = width

        self.dims = glm.vec3(self.x, self.y, self.z)

    @cached_property
    def box_offsets(self):
        return tuple(offset * self.dims for offset in self.__box_offsets)

    def __iter__(self):
        return self.box_offsets


class Mover:
    pass
