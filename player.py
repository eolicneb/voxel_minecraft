import glm
import pygame as pg
from camera import Camera
from mobile import Movable, Mobile
from action_controller import ActionController
from settings import *


class Player(Movable):
    def __init__(self, app, position=PLAYER_POS, yaw=-90, pitch=0, pg=pg):
        self.app = app
        self.pg = pg
        super().__init__(
            position=Mobile(position, glm.radians(yaw), glm.radians(pitch)),
            accel=Mobile(glm.vec3(0, GRAVITY_ACCEL, 0), 0, 0)
        )
        self.camera = Camera(self.position)
        self.action_controller = ActionController(self,
                                                  buoyancy=PLAYER_BUOYANCY,
                                                  jump_velocity=PLAYER_JUMP_VEL)

    def __str__(self):
        obj_str = super().__str__()[:-2]
        obj_str += f"\n  action_controller: {self.action_controller}\n>"
        return obj_str

    def update(self):
        self.action_controller.update()
        old_pos = self.position.copy()
        self.keyboard_speed_control()
        # self.keyboard_control()
        self.mouse_control()
        self.set_tick(self.app.delta_time)
        super().update()
        if self.position != old_pos:
            self.camera.update()

    def handle_event(self, event):
        # adding and removing voxels with clicks
        if event.type == self.pg.MOUSEBUTTONDOWN:
            voxel_handler = self.app.scene.world.voxel_handler
            if event.button == 1:
                voxel_handler.set_voxel()
            if event.button == 3:
                voxel_handler.switch_mode()

    def mouse_control(self):
        mouse_dx, mouse_dy = self.pg.mouse.get_rel()
        if mouse_dx:
            self.position.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.position.rotate_pitch(delta_y=mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = self.pg.key.get_pressed()
        vel = PLAYER_SPEED * self.app.delta_time
        if key_state[self.pg.K_w]:
            self.position.move_forward(vel)
        if key_state[self.pg.K_s]:
            self.position.move_back(vel)
        if key_state[self.pg.K_d]:
            self.position.move_right(vel)
        if key_state[self.pg.K_a]:
            self.position.move_left(vel)
        if key_state[self.pg.K_q]:
            self.position.move_up(vel)
        if key_state[self.pg.K_e]:
            self.position.move_down(vel)

    def keyboard_speed_control(self):
        key_state = self.pg.key.get_pressed()
        new_vel = glm.vec3(0., 0., 0.)
        if self.action_controller.is_standing or self.action_controller.is_swimming or self.action_controller.is_flying:
            if key_state[self.pg.K_w]:
                new_vel.x += 1
            if key_state[self.pg.K_s]:
                new_vel.x -= 1
            if key_state[self.pg.K_d]:
                new_vel.z += 1
            if key_state[self.pg.K_a]:
                new_vel.z -= 1
            if not self.action_controller.is_standing:
                if key_state[self.pg.K_q]:
                    new_vel.y += 1
                if key_state[self.pg.K_e]:
                    new_vel.y -= 1
            speed = PLAYER_SPEED * self.app.delta_time
            if self.action_controller.is_swimming:
                speed *= .3  # TODO move to settings
            if any(new_vel):
                new_vel = glm.normalize(new_vel)
            self.speed_forward(new_vel * speed)
        if self.action_controller.is_standing:
            if key_state[self.pg.K_SPACE]:
                self.action_controller.jump()
