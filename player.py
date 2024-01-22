import pygame as pg
from camera import Camera
from mobile import Movable, Mobile
from settings import *


class Player(Movable):
    def __init__(self, app, position=PLAYER_POS, yaw=-90, pitch=0):
        self.app = app
        super().__init__(
            position=Mobile(position, glm.radians(yaw), glm.radians(pitch)),
            # accel=Mobile(glm.vec3(0, -0.000006, 0), 0, 0)
        )
        self.camera = Camera(self.position)

    def update(self):
        self.set_tick(self.app.delta_time)
        self.keyboard_control()
        self.mouse_control()
        super().update()
        self.camera.update()

    def handle_event(self, event):
        # adding and removing voxels with clicks
        if event.type == pg.MOUSEBUTTONDOWN:
            voxel_handler = self.app.scene.world.voxel_handler
            if event.button == 1:
                voxel_handler.set_voxel()
            if event.button == 3:
                voxel_handler.switch_mode()

    def mouse_control(self):
        mouse_dx, mouse_dy = pg.mouse.get_rel()
        if mouse_dx:
            self.position.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.position.rotate_pitch(delta_y=mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = pg.key.get_pressed()
        vel = PLAYER_SPEED * self.app.delta_time
        if key_state[pg.K_w]:
            self.position.move_forward(vel)
        if key_state[pg.K_s]:
            self.position.move_back(vel)
        if key_state[pg.K_d]:
            self.position.move_right(vel)
        if key_state[pg.K_a]:
            self.position.move_left(vel)
        if key_state[pg.K_q]:
            self.position.move_up(vel)
        if key_state[pg.K_e]:
            self.position.move_down(vel)
