from settings import *
from frustum import Frustum


class Camera:
    def __init__(self, mobile):
        self.mobile = mobile
        self.position = self.mobile.location

        self.m_proj = glm.perspective(V_FOV, ASPECT_RATIO, NEAR, FAR)
        self.m_view = glm.mat4()

        self.frustum = Frustum(self.mobile)

    def update(self):
        self.m_view = glm.lookAt(self.mobile.location, self.mobile.location + self.mobile.forward, self.mobile.up)
