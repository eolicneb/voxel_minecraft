from __future__ import annotations
from copy import copy

from settings import *


class Mobile:
    def __init__(self, position, yaw, pitch):
        self.location = glm.vec3(position)
        self.yaw = yaw
        self.pitch = pitch

        self._rot = glm.mat4()
        self._rot_horiz = glm.mat4()

    def update_rotation(self):
        rot = glm.mat4(1.0)
        self._rot_horiz = glm.rotate(rot, self.yaw, -Y)
        self._rot = glm.rotate(self._rot_horiz, self.pitch, Z)

    @property
    def x(self):
        return self.location.x

    @property
    def y(self):
        return self.location.y

    @property
    def z(self):
        return self.location.z

    @property
    def norm(self):
        return glm.l2Norm(self.location)

    @property
    def forward(self):
        return self._rot[0].xyz

    @property
    def right(self):
        return self._rot[2].xyz

    @property
    def up(self):
        return self._rot[1].xyz

    def copy(self):
        new_obj = self.__class__(copy(self.location), self.yaw, self.pitch)
        new_obj._rot = self._rot
        return new_obj

    def update(self):
        self.update_rotation()

    def rotate(self, vec: glm.vec3):
        return (self._rot * vec).xyz

    def rotate_planar(self, vec: glm.vec3):
        return (self._rot_horiz * vec).xyz

    def get_model_matrix(self):
        # m_model = self._rot
        m_model = glm.translate(glm.mat4(1.0), self.location) * self._rot
        # m_model = glm.translate(m_model, glm.vec3(3, 15, 0))
        return m_model

    def rotate_pitch(self, delta_y):
        self.pitch -= delta_y
        self.pitch = glm.clamp(self.pitch, -PITCH_MAX, PITCH_MAX)

    def rotate_yaw(self, delta_x):
        self.yaw += delta_x

    def move_left(self, velocity):
        self.location -= self.right * velocity

    def move_right(self, velocity):
        self.location += self.right * velocity

    def move_up(self, velocity):
        self.location += self.up * velocity

    def move_down(self, velocity):
        self.location -= self.up * velocity

    def move_forward(self, velocity):
        self.location += self.forward * velocity

    def move_back(self, velocity):
        self.location -= self.forward * velocity

    def set_from(self, other):
        self.location = copy(other.location)
        self.yaw = other.yaw
        self.pitch = other.pitch
        self._rot = other._rot

    def __add__(self, other: Mobile):
        new_obj = self.copy()
        if isinstance(other, Mobile):
            new_obj.yaw += other.yaw
            new_obj.pitch += other.pitch
            new_obj.location += other.location
        else:
            x, y, z = other
            new_obj.location.x += x
            new_obj.location.y += y
            new_obj.location.z += z
        return new_obj

    def __iadd__(self, other):
        new_obj = self + other
        self.set_from(new_obj)
        return self

    def __mul__(self, other):
        new_obj = self.copy()
        new_obj.location *= other
        new_obj.yaw *= other
        new_obj.pitch *= other
        return new_obj

    def __imul__(self, other):
        new_obj = self * other
        self.set_from(new_obj)
        return self

    def __eq__(self, other):
        return self.location == other.location and self.yaw == other.yaw and self.pitch == other.pitch

    def __iter__(self):
        return iter((self.location.x, self.location.y, self.location.z))

    def __str__(self):
        return f"<{self.x:5.1f}, {self.y:5.1f}, {self.z:5.1f} | yaw: {self.yaw:5.1f}, pitch: {self.pitch:5.1f}>"


class Movable:
    def __init__(self, position: Mobile = None, velocity: Mobile = None, accel: Mobile = None):
        self.position = position if position is not None else Mobile(glm.vec3(0, 0, 0), 0, 0)
        self.velocity = velocity if velocity is not None else Mobile(glm.vec3(0, 0, 0), 0, 0)
        self.accel = accel if accel is not None else Mobile(glm.vec3(0, 0, 0), 0, 0)

        self.delta_t: float = 0

    def __str__(self):
        obj_str = f"<{self.__class__.__name__}"
        obj_str += f"\n  position: {self.position}"
        obj_str += f"\n  velocity: {self.velocity}"
        obj_str += f"\n  accel: {self.accel}\n>"
        return obj_str

    def speed_forward(self, vel_vector):
        self.velocity.location = self.position.rotate(vel_vector)

    def speed_horizontal(self, vel_vector):
        self.velocity.location = self.position.rotate_planar(vel_vector)

    def set_tick(self, delta_t: float):
        self.delta_t = delta_t

    def update(self):
        self.position += self.velocity * self.delta_t
        self.velocity += self.accel * self.delta_t
        self.position.pitch = glm.clamp(self.position.pitch, -PITCH_MAX, PITCH_MAX)
        self.position.yaw %= (2 * math.pi)
        self.position.update()
        self.velocity.update()
        self.accel.update()

    def copy(self):
        new_obj = Movable(position=self.position.copy(),
                          velocity=self.velocity.copy(),
                          accel=self.accel.copy())
        new_obj.delta_t = self.delta_t
        return new_obj


@njit
def engross(pos: Mobile, h_size: glm.vec3
            ) -> list[glm.vec3]:
    offsets = [(1, -1, 1), (-1, -1, 1), (-1, -1, -1), (1, -1, 1),
               (1, 1, 1), (-1, 1, 1), (-1, 1, -1), (1, 1, 1)]
    vertices = np.array(offsets, dtype=np.float32)
    return vertices * h_size + pos


class Crushable:
    def __init__(self, movable, dimensions):
        self.position = movable.position
        self.movable = movable
        self.dimensions = dimensions  # (depth, height, width)
        self._h_dim = glm.vec3(*(x/2 for x in self.dimensions))

    def vertices(self):
        displace = self.position.rotate(self._h_dim).xyz
        offsets = [(1, -1, 1), (-1, -1, 1), (-1, -1, -1), (1, -1, 1),
                   (1, 1, 1), (-1, 1, 1), (-1, 1, -1), (1, 1, 1)]
        return [self.position.location + displace * offset
                for offset in offsets]


if __name__ == "__main__":
    pos = Mobile(glm.vec3(1, 1, 1), glm.radians(-90), 0)
    for coord in pos:
        assert coord == 1

    accel = Mobile(glm.vec3(1, -1, 0), 0.5, 0.1)
    initial = Movable(position=pos, accel=accel)

    # test speed_forward
    initial.position.rotate_yaw(1.0)
    for _ in range(5):
        initial.speed_forward(glm.vec3(1, 1, 1))
        print(initial.velocity)

    movable = initial.copy()
    movable.set_tick(0.1)
    movable.update()
    assert movable.position == initial.position
    movable.update()
    assert not movable.position == initial.position
    assert movable.position.y < initial.position.y

    movable = initial.copy()
    movable.set_tick(0.1)
    movable.position.rotate_yaw(1.0)
    assert movable.position.yaw == initial.position.yaw + 1.0, "before update"
    initial.update()
    assert movable.position.yaw == initial.position.yaw + 1.0, "after update initial"
    movable.update()
    assert movable.position.yaw == initial.position.yaw + 1.0, "after update movable"
    assert sum(movable.position.forward * movable.position.right) == 0.0

    # Test crushable
    pos_0 = glm.vec3(1, 1, 1)
    size = glm.vec3(2, 4, 1)
    crush = Crushable(Movable(Mobile(pos_0, glm.radians(90), glm.radians(45))), size)
    vertices = crush.vertices()
    assert glm.l2Norm(vertices[0] - vertices[6]) == glm.l2Norm(size)
    assert glm.l2Norm(glm.cross(crush.position.forward, vertices[0] - vertices[1])) == 0.0
