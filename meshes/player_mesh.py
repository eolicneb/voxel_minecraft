from meshes.base_mesh import BaseMesh


class MoverMesh(BaseMesh):
    def __init__(self, mover):
        super().__init__()
        self.ctx = mover.app.ctx
        self.program = getattr(mover.app.shader_program, mover.name)
