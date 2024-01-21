from meshes.base_plane_mesh import BasePlaneMesh
from settings import *


class Bedrock:
    def __init__(self, scene):
        self.name = "bedrock"
        self.app = scene.app
        self.level = 0
        self.extension = 5 * CHUNK_SIZE * WORLD_W
        self.mesh = BasePlaneMesh(self)

    def render(self):
        self.mesh.render()
