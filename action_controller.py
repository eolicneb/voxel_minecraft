from settings import *

from time import time


class ActionController:
    def __init__(self, movable, *,
                 mass=None,
                 advance_velocity=None,
                 jump_velocity=None,
                 swim_velocity=None,
                 buoyancy=None,
                 flight_velocity=None):
        self.movable = movable

        self.mass = mass
        self.advance_velocity = advance_velocity
        self.jump_velocity = jump_velocity
        self.swim_velocity = swim_velocity
        self.buoyancy = buoyancy
        self.flight_velocity = flight_velocity

        self.is_advancing = False
        self.is_jumping = False
        self.is_swimming = False
        self.is_flying = False
        self.is_standing = False

    def __str__(self):
        obj_str = f"<{self.__class__.__name__}"
        obj_str += f"\n  is_advancing: {self.is_advancing}"
        obj_str += f"\n  is_jumping: {self.is_jumping}"
        obj_str += f"\n  is_swimming: {self.is_swimming}"
        obj_str += f"\n  is_flying: {self.is_flying}"
        obj_str += f"\n  is_standing: {self.is_standing}\n>"
        return obj_str

    def stand_on_ground(self):
        ground_pos = int(self.movable.position.location.y)
        self.movable.position.location.y = ground_pos + AVOIDANCE
        self.movable.velocity.location.y = 0
        self.movable.accel.location.y = 0
        self.is_standing = True
        self.is_flying = False
        self.is_jumping = False

    def jump(self):
        if not self.jump_velocity or not self.is_standing:
            print(f"{time():.1f} Couldnt jump")
            return
        print(f"{time():.1f} jumping")
        self.is_jumping = True
        self.movable.velocity.location.y = self.jump_velocity
        self.is_standing = False
        self.update()

    def fly(self):
        self.is_flying = True
        self.movable.accel.y = 0

    def update(self):
        if not self.is_standing:
            if self.is_swimming:
                # print(self.movable.velocity, self.movable.accel)
                self.movable.accel.location = self.movable.velocity.location * (-.001, -.001, -.001)
                self.movable.accel.location.y = GRAVITY_ACCEL * (1 - self.buoyancy)
            elif not self.is_flying:
                self.movable.accel.location.y = GRAVITY_ACCEL


