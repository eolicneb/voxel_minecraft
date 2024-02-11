import pickle
from pathlib import Path

from settings import *
from world_objects.chunk import Chunk
from voxel_handler import VoxelHandler


class Cache:
    def __init__(self, cache_file_name: str = None):
        self.file = cache_file_name and Path(cache_file_name + ".pkl")

    def save(self, obj):
        if not self.file:
            return
        with self.file.open("wb") as f:
            pickle.dump(obj, f, -1)

    def load(self):
        if not self.file or not self.file.exists():
            return None
        with self.file.open("rb") as f:
            return pickle.load(f)


cache = Cache()


class World:
    def __init__(self, app):
        self.app = app
        self.chunks: list[Chunk | None] = [None for _ in range(WORLD_VOL)]
        self.voxels = np.empty([WORLD_VOL, CHUNK_VOL], dtype='uint8')
        self.build_chunks()
        self.build_chunk_mesh()
        self.voxel_handler = VoxelHandler(self)

    @staticmethod
    def pos_chunk_index(x, y, z):
        ch_x, ch_y, ch_z = x // CHUNK_SIZE, y // CHUNK_SIZE, z // CHUNK_SIZE
        return ch_x + WORLD_W * ch_z + WORLD_AREA * ch_y

    @staticmethod
    def pos_voxel_index(x, y, z):
        vx_x, vx_y, vx_z = x % CHUNK_SIZE, y % CHUNK_SIZE, z % CHUNK_SIZE
        return vx_x + CHUNK_SIZE * vx_z + CHUNK_AREA * vx_y

    def build_chunks(self):
        if cached := cache.load():
            self.voxels, self.chunks = cached
        else:
            self.__build_chunks()
            cache.save((self.voxels, self.chunks))

    def __build_chunks(self):
        for x in range(WORLD_W):
            for y in range(WORLD_H):
                for z in range(WORLD_D):
                    chunk = Chunk(self, position=(x, y, z))

                    ch_index = x + WORLD_W * z + WORLD_AREA * y
                    self.chunks[ch_index] = chunk

                    # put the chunk voxels in a separate array
                    self.voxels[ch_index] = chunk.build_voxels()

                    # get pointer to voxels
                    chunk.voxels = self.voxels[ch_index]

    def build_chunk_mesh(self):
        for chunk in self.chunks:
            chunk.build_mesh()

    def update(self):
        self.voxel_handler.update()

    def render(self):
        for chunk in self.chunks:
            chunk.render()

    def render_see_through(self):
        for chunk in self.chunks:
            chunk.render_see_through()

    def position_block(self, x, y, z):
        x, y, z = int(x), int(y), int(z)
        chunk_index = self.pos_chunk_index(x, y, z)
        voxel_index = self.pos_voxel_index(x, y, z)
        try:
            return self.voxels[chunk_index][voxel_index]
        except IndexError:
            return AIR
        except Exception as e:
            print(f"{e} {chunk_index} ({type(chunk_index)}) | {voxel_index} ({type(voxel_index)})")


if __name__ == "__main__":
    class FakeWorld:
        """self.app.player.camera.frustum.is_on_frustum"""
        class player:
            class camera:
                class frustum:
                    @staticmethod
                    def is_on_frustum(*args):
                        pass
        class ctx:
            @staticmethod
            def buffer(*args):
                pass
            @staticmethod
            def vertex_array(*args, **kwargs):
                pass
        class shader_program:
            chunk = None
    world = World(FakeWorld)
    print("chunk size", CHUNK_SIZE)
    offsets = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    for offset in offsets:
        for delta in range(10):
            delta_offset = [delta / 3 * o for o in offset]
            x, y, z = [c + o for c, o in zip(PLAYER_POS, delta_offset)]
            i_x, i_y, i_z = [int(c) for c in (x, y, z)]
            print("\nposition", x, type(x), y, type(y), z, type(z))
            print("int(position)", i_x, type(i_x), i_y, type(i_y), i_z, type(i_z))
            ch_ix, vx_ix = world.pos_chunk_index(i_x, i_y, i_z), world.pos_voxel_index(i_x, i_y, i_z)
            print("block", world.position_block(i_x, i_y, i_z))
            print("indexes", ch_ix, type(ch_ix), vx_ix, type(vx_ix))
