from meshes.base_plane_mesh import BasePlaneMesh
from settings import *
from meshes.water_mesh import WaterMesh


class Water:
    def __init__(self, scene):
        self.name = "water"
        self.app = scene.app
        self.level = WATER_LINE
        self.extension = 5 * CHUNK_SIZE * WORLD_W
        self.mesh = BasePlaneMesh(self)

    def render(self):
        self.mesh.render()
