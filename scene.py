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

        self.mobs = {}

    def register_mob(self, mob_id, mob):
        self.mobs[mob_id] = mob

    def pop_mob(self, mob_id):
        if mob_id not in self.mobs:
            return
        return self.mobs.pop(mob_id)

    def update(self):
        self.world.update()
        for mob in self.mobs.values():
            mob.update()
        self.voxel_marker.update()

    def render(self):
        self.bedrock.render()
        self.world.render()
        for mob in self.mobs.values():
            mob.render()
        self.world.render_see_through()
        for mob in self.mobs.values():
            if hasattr(mob, "render_see_through"):
                mob.render_see_through()

        # rendering without cull face
        self.app.ctx.disable(mgl.CULL_FACE)
        self.water.render()
        self.app.ctx.enable(mgl.CULL_FACE)

        self.voxel_marker.render()
