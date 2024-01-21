import moderngl as mgl

from world import World
from world_objects.bedrock import Bedrock
from world_objects.voxel_marker import VoxelMarker
from world_objects.water import Water


class Scene:
    def __init__(self, app):
        self.app = app
        self.world = World(self.app)
        self.voxel_marker = VoxelMarker(self.world.voxel_handler)

        self.bedrock = Bedrock(self)
        self.water = Water(self)

    def update(self):
        self.world.update()
        self.voxel_marker.update()

    def render(self):
        self.bedrock.render()
        self.world.render()
        self.world.render_see_through()

        # rendering without cull face
        self.app.ctx.disable(mgl.CULL_FACE)
        self.water.render()
        self.app.ctx.enable(mgl.CULL_FACE)

        self.voxel_marker.render()
