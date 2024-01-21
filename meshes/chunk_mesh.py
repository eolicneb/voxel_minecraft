import settings
from meshes.base_mesh import BaseMesh
from meshes.chunk_mesh_builder import build_chunk_mesh


class FixedChunkMesh(BaseMesh):
    def __init__(self, ctx, program, vertex_data):
        super().__init__()
        self.ctx = ctx
        self.program = program

        self.vbo_format = '1u4'
        self.format_size = sum(int(fmt[:1]) for fmt in self.vbo_format.split())
        self.attrs = ('packed_data',)

        self.vertex_data = vertex_data

    def get_vertex_data(self):
        return self.vertex_data


class ChunkMesh(BaseMesh):
    def __init__(self, chunk):
        super().__init__()
        self.app = chunk.app
        self.chunk = chunk
        self.ctx = self.app.ctx
        self.program = self.app.shader_program.chunk

        self.vbo_format = '1u4'
        self.format_size = sum(int(fmt[:1]) for fmt in self.vbo_format.split())
        self.attrs = ('packed_data',)

        self.solid_mesh = FixedChunkMesh(self.ctx, self.program, None)
        self.see_through_mesh = FixedChunkMesh(self.ctx, self.program, None)

        self.update_vao()

    def update_vao(self):
        super().update_vao()
        self.solid_mesh.update_vao()
        self.see_through_mesh.update_vao()

    def rebuild(self):
        self.update_vao()

    def get_vertex_data(self):
        solid, see_through = build_chunk_mesh(
            chunk_voxels=self.chunk.voxels,
            format_size=self.format_size,
            chunk_pos=self.chunk.position,
            world_voxels=self.chunk.world.voxels,
            see_through_blocks=settings.SEE_THROUGH_BLOCKS
        )
        self.solid_mesh.vertex_data = solid
        self.see_through_mesh.vertex_data = see_through
        return None

    def render(self):
        self.solid_mesh.render()

    def render_see_through(self):
        self.see_through_mesh.render()
