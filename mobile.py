from __future__ import annotations
from copy import copy

from settings import *


@njit
def normalize(vector):
    # Compute the magnitude of the vector
    mag = np.linalg.norm(vector)

    # Check if the magnitude is nonzero
    if mag != 0:
        # Divide each component by the magnitude to get the normalized vector
        return vector / mag
    else:
        # Return a zero vector (which is already normalized)
        return np.zeros_like(vector)


@njit
def normalize_vectors(yaw, pitch):
    x = math.cos(yaw) * math.cos(pitch)
    y = math.sin(pitch)
    z = math.sin(yaw) * math.cos(pitch)

    forward = normalize(np.array((x, y, z), dtype=np.float64))
    right = normalize(np.cross(forward, np.array((0, 1, 0))))
    up = normalize(np.cross(right, forward))
    return up, right, forward


class Mobile:
    def __init__(self, position, yaw, pitch):
        self.position = glm.vec3(position)
        self.yaw = yaw
        self.pitch = pitch

        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, 1)

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    @property
    def z(self):
        return self.position.z

    def copy(self):
        new_obj = self.__class__(copy(self.position), self.yaw, self.pitch)
        new_obj.up = self.up
        new_obj.right = self.right
        new_obj.forward = self.forward
        return new_obj

    def update(self):
        self.update_vectors()

    def update_vectors(self):
        up, right, forward = normalize_vectors(self.yaw, self.pitch)
        self.up = glm.vec3(up)
        self.right = glm.vec3(right)
        self.forward = glm.vec3(forward)

    # def update_vectors(self):
    #     self.forward.x = glm.cos(self.yaw) * glm.cos(self.pitch)
    #     self.forward.y = glm.sin(self.pitch)
    #     self.forward.z = glm.sin(self.yaw) * glm.cos(self.pitch)
    #
    #     self.forward = glm.normalize(self.forward)
    #     self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
    #     self.up = glm.normalize(glm.cross(self.right, self.forward))

    def rotate_pitch(self, delta_y):
        self.pitch -= delta_y
        self.pitch = glm.clamp(self.pitch, -PITCH_MAX, PITCH_MAX)

    def rotate_yaw(self, delta_x):
        self.yaw += delta_x

    def move_left(self, velocity):
        self.position -= self.right * velocity

    def move_right(self, velocity):
        self.position += self.right * velocity

    def move_up(self, velocity):
        self.position += self.up * velocity

    def move_down(self, velocity):
        self.position -= self.up * velocity

    def move_forward(self, velocity):
        self.position += self.forward * velocity

    def move_back(self, velocity):
        self.position -= self.forward * velocity

    def set_from(self, other):
        self.position = copy(other.position)
        self.yaw = other.yaw
        self.pitch = other.pitch
        self.forward = other.forward
        self.right = other.right
        self.up = other.up

    def __add__(self, other: Mobile):
        new_obj = self.copy()
        new_obj.position += other.position
        new_obj.yaw += other.yaw
        new_obj.pitch += other.pitch
        new_obj.update()
        return new_obj

    def __iadd__(self, other):
        new_obj = self + other
        self.set_from(new_obj)
        return self

    def __mul__(self, other):
        new_obj = self.copy()
        new_obj.position *= other
        new_obj.yaw *= other
        new_obj.pitch *= other
        new_obj.update()
        return new_obj

    def __imul__(self, other):
        new_obj = self * other
        self.set_from(new_obj)
        return self

    def __eq__(self, other):
        return self.position == other.position and self.yaw == other.yaw and self.pitch == other.pitch


class Movable:
    def __init__(self, position: Mobile = None, velocity: Mobile = None, accel: Mobile = None):
        self.position = position if position is not None else Mobile(glm.vec3(0, 0, 0), 0, 0)
        self.velocity = velocity if velocity is not None else Mobile(glm.vec3(0, 0, 0), 0, 0)
        self.accel = accel if accel is not None else Mobile(glm.vec3(0, 0, 0), 0, 0)

        self.delta_t: float = 0

    def set_tick(self, delta_t: float):
        self.delta_t = delta_t

    def update(self):
        self.position += self.velocity * self.delta_t
        self.velocity += self.accel * self.delta_t
        self.position.pitch = glm.clamp(self.position.pitch, -PITCH_MAX, PITCH_MAX)

    def copy(self):
        new_obj = Movable(position=self.position.copy(),
                          velocity=self.velocity.copy(),
                          accel=self.accel.copy())
        new_obj.delta_t = self.delta_t
        return new_obj


if __name__ == "__main__":
    n = normalize(np.array((1., 1., 1.)))
    assert np.linalg.norm(n) == 1.0

    _, _, forward = normalize_vectors(0, 0)
    assert forward.dot(np.array((1, 0, 0))) == 1.

    _, _, forward = normalize_vectors(np.pi/2, 0)
    assert forward.dot(np.array((0, 0, 1))) == 1.

    _, right, forward = normalize_vectors(np.pi/4, 0)
    assert forward.dot(np.array((0, 0, 1))) == right.dot(np.array((0, 0, 1)))

    pos = Mobile(glm.vec3(1, 1, 1), glm.radians(-90), 0)

    accel = Mobile(glm.vec3(1, -1, 0), 0.5, 0.1)
    initial = Movable(position=pos, accel=accel)

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
