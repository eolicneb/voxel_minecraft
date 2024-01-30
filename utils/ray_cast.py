from collections import namedtuple
from typing import Iterable

import glm


ray_cast_step = namedtuple('RayCastStep', 'max_x max_y max_z step_dir')


class RayCast:
    HUGE = 10000000.0
    
    def __init__(self,
                 origin: Iterable,
                 direction: Iterable = None,
                 destination: Iterable = None,
                 max_ray_dist: float = 0.):

        assert direction is None and destination is None, f"{self.__class__.__name__} can not accept both direction and destination"

        self.origin = origin if isinstance(origin, glm.vec3) else glm.vec3(*origin)
        self.x1, self.y1, self.z1 = origin

        if destination is not None:
            self.dest = destination if isinstance(destination, glm.vec3) else glm.vec3(*destination)
        else:
            raise ValueError("destination is None")
        self.x2, self.y2, self.z2 = self.dest

        self.limit = max_ray_dist or glm.l1Norm(self.dest - self.origin)

        self.dx = None
        self.delta_x = None
        self.max_x = None
        self.dy = None
        self.delta_y = None
        self.max_y = None
        self.dz = None
        self.delta_z = None
        self.max_z = None

        self.step_dir = None
        self.current_voxel_pos = None

    def __iter__(self):
        self.dx = glm.sign(self.x2 - self.x1)
        self.delta_x = min(self.dx / (self.x2 - self.x1), self.HUGE) if self.dx != 0 else self.HUGE
        self.max_x = self.delta_x * (1.0 - glm.fract(self.x1)) if self.dx > 0 else self.delta_x * glm.fract(self.x1)
        
        self.dy = glm.sign(self.y2 - self.y1)
        self.delta_y = min(self.dy / (self.y2 - self.y1), self.HUGE) if self.dy != 0 else self.HUGE
        self.max_y = self.delta_y * (1.0 - glm.fract(self.y1)) if self.dy > 0 else self.delta_y * glm.fract(self.y1)
        
        self.dz = glm.sign(self.z2 - self.z1)
        self.delta_z = min(self.dz / (self.z2 - self.z1), self.HUGE) if self.dz != 0 else self.HUGE
        self.max_z = self.delta_z * (1.0 - glm.fract(self.z1)) if self.dz > 0 else self.delta_z * glm.fract(self.z1)
        
        self.step_dir = -1
        self.current_voxel_pos = self.origin

        return self

    def __next__(self):

        if ((self.max_x > 1.0 and self.max_y > 1.0 and self.max_z > 1.0)
                or (self.current_voxel_pos - self.origin > self.limit)):
            return

        if self.max_x < self.max_y:
            if self.max_x < self.max_z:
                self.current_voxel_pos.x += self.dx
                self.max_x += self.delta_x
                self.step_dir = 0
            else:
                self.current_voxel_pos.z += self.dz
                self.max_z += self.delta_z
                self.step_dir = 2
        else:
            if self.max_y < self.max_z:
                self.current_voxel_pos.y += self.dy
                self.max_y += self.delta_y
                self.step_dir = 1
            else:
                self.current_voxel_pos.z += self.dz
                self.max_z += self.delta_z
                self.step_dir = 2

    @property
    def voxel_normal(self):
        if self.step_dir is None:
            return
        voxel_normal = glm.ivec3(0)
        if self.step_dir == 0:
            voxel_normal.x = -self.dx
        elif self.step_dir == 1:
            voxel_normal.y = -self.dy
        else:
            voxel_normal.z = -self.dz
        return voxel_normal
