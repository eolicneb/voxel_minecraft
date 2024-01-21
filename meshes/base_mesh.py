import numpy as np


class BaseMesh:
    class DontRender(Exception):
        """Skips mesh rendering"""

    def __init__(self):
        # OpenGL context
        self.ctx = None
        # shader program
        self.program = None
        # vertex buffer data type format: "3f 3f"
        self.vbo_format = None
        # attribute names according to the format: ("in_position", "in_color")
        self.attrs: tuple[str, ...] = None
        # vertex array object
        self.vao = None

    def get_vertex_data(self) -> np.array: ...

    def update_vao(self):
        vertex_data = self.get_vertex_data()
        if vertex_data is None:
            return
        vbo = self.ctx.buffer(vertex_data)
        self.vao = self.ctx.vertex_array(
            self.program, [(vbo, self.vbo_format, *self.attrs)], skip_errors=True
        )
        return self.vao

    def render(self):
        if self.vao:
            self.vao.render()
