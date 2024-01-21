from settings import *
from meshes.base_mesh import BaseMesh


class BasePlaneMesh(BaseMesh):
    def __init__(self, plane):
        super().__init__()
        self.plane = plane
        self.app = plane.app
        self.ctx = plane.app.ctx
        self.program = getattr(plane.app.shader_program, self.plane.name)

        self.vbo_format = '3f2 2f2'
        self.attrs = ('in_position', 'in_tex_coord_0')
        self.update_vao()

    def get_vertex_data(self) -> np.array:
        y = self.plane.level
        (x0, z0), (x1, z1) = self.get_plane_vertices()
        vertex_data = np.array(
            [
                (x0, y, z0), (x0, y, z1), (x1, y, z1),
                (x0, y, z0), (x1, y, z1), (x1, y, z0),
            ],
            dtype='float16'
        )
        uv_coord = np.array(
            [
                (x0, z0), (x0, z1), (x1, z1),
                (x0, z0), (x1, z1), (x1, z0),
            ],
            dtype='float16'
        )
        return np.hstack([vertex_data, uv_coord])

    def get_plane_vertices(self):
        h_extension = self.plane.extension // 2
        return (-h_extension, -h_extension), (h_extension, h_extension)
