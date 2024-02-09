import sys
from time import time
from traceback import format_exc
from copy import copy

from settings import *


class PhysicsEngine:
    def __init__(self, world):
        self.world = world
        self.movables = set()

    def register_movable(self, movable):
        self.movables.add(movable)

    def update_movable(self, movable):
        old_pos = movable.position.copy()
        movable.update()
        self.allow_movement(movable, old_pos)
        if hasattr(movable, "camera"):
            movable.camera.update()

    def update(self):
        for movable in self.movables:
            self.update_movable(movable)

    def handle_event(self, event):
        for movable in self.movables:
            old_pos = movable.position.copy()
            movable.handle_event(event)
            self.allow_movement(movable, old_pos)

    def allow_movement(self, movable, old_pos):
        try:
            if old_pos.location.y > HEIGHT_LIMIT:
                movable.position.location.y = HEIGHT_LIMIT
                movable.action_controller.is_standing = False
                return

            if (check_block := self.world.position_block(*old_pos.location)) not in MOVE_THROUGH_BLOCKS:
                while check_block not in MOVE_THROUGH_BLOCKS:
                    old_pos.location.y += AVOIDANCE
                    check_block = self.world.position_block(*old_pos.location)
                movable.position.location = copy(old_pos.location)
                movable.action_controller.stand_on_ground()
                return

            if movable.position.location == old_pos.location:
                return

            new_pos = movable.position
            range_vec = new_pos.location - old_pos.location
            direction = tuple(1 if c > 0 else -1 for c in range_vec)
            norm = int(max(range_vec * direction)) + 3
            step_vec = range_vec / norm
            step_pos = copy(old_pos.location)

            for f in range(1, norm + 1):
                step_pos += step_vec
                if (check_block := self.world.position_block(*step_pos)) not in MOVE_THROUGH_BLOCKS:
                    new_pos.location = old_pos.location
                    break
                old_pos.location = step_pos

            # move away from walls
            int_pos = int(new_pos.x), int(new_pos.y), int(new_pos.z)
            for i, axis in enumerate(((1, 0, 0), (0, 1, 0), (0, 0, 1))):
                for add, sign in ((0, -1), (1, 1)):
                    offset = tuple(sign * coord for coord in axis)
                    check_pos = (c + o for c, o in zip(int_pos, offset))
                    if self.world.position_block(*check_pos) not in MOVE_THROUGH_BLOCKS:
                        if (int_pos[i] + add - new_pos.location[i]) * sign < AVOIDANCE:
                            new_pos.location[i] = int_pos[i] + add - AVOIDANCE * sign
                        break

            dist_to_ground, block = self.distance_to_ground(*new_pos.location)
            if dist_to_ground is not None and dist_to_ground < AVOIDANCE + 0.1:
                old_velocity = movable.velocity.copy()
                if old_velocity.norm > 10 and False:
                    movable.velocity.location *= (.5, -.5, .5)
                else:
                    movable.velocity.location.y = 0
                    movable.action_controller.stand_on_ground()
            else:
                movable.action_controller.is_standing = False

            if new_pos.y < WATER_LINE:
                movable.action_controller.is_swimming = True
            elif new_pos.y > WATER_LINE and movable.action_controller.is_swimming:
                movable.action_controller.is_swimming = False

        except:
            raise
            # print(format_exc())
            # for var, val in locals().items():
            #     if var.startswith("__"):
            #         continue
            #     print(f"{var}: <{type(val)}> {val}")
            # sys.exit()

    def distance_to_ground(self, x, y, z) -> [float | None, int]:
        if block := self.world.position_block(x, y - 1, z) in MOVE_THROUGH_BLOCKS:
            return None, block
        else:
            return (y - int(y) - AVOIDANCE) / (1 - AVOIDANCE), block
