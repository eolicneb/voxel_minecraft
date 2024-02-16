from numba import njit
import numpy as np
import glm
import math

# resolution
WIN_RES = glm.vec2(3200, 1800)

# world generation
SEED = 18

# global axis
X = glm.vec3(1, 0, 0)
Y = glm.vec3(0, 1, 0)
Z = glm.vec3(0, 0, 1)
FORWARD, UP, RIGHT = X, Y, Z

# ray casting
MAX_RAY_DIST = 6

# chunk
CHUNK_SIZE = 60
# CHUNK_SIZE = 30
H_CHUNK_SIZE = CHUNK_SIZE // 2
CHUNK_AREA = CHUNK_SIZE * CHUNK_SIZE
CHUNK_VOL = CHUNK_AREA * CHUNK_SIZE
CHUNK_SPHERE_RADIUS = H_CHUNK_SIZE * math.sqrt(3)

# world
WORLD_W, WORLD_H = 20, 3
# WORLD_W, WORLD_H = 2, 2
WORLD_D = WORLD_W
WORLD_AREA = WORLD_W * WORLD_D
WORLD_VOL = WORLD_AREA * WORLD_H

# world center
CENTER_XZ = WORLD_W * H_CHUNK_SIZE
CENTER_Y = WORLD_H * H_CHUNK_SIZE

# camera
ASPECT_RATIO = WIN_RES.x / WIN_RES.y
FOV_DEG = 50
V_FOV = glm.radians(FOV_DEG)  # vertical FOV
H_FOV = 2 * math.atan(math.tan(V_FOV * 0.5) * ASPECT_RATIO)  # horizontal FOV
NEAR = 0.1
FAR = 2000.0
PITCH_MAX = glm.radians(89)

# colors
BG_COLOR = glm.vec3(0.58, 0.83, 0.99)

# textures
AIR = 0
SAND = 1
GRASS = 2
DIRT = 3
STONE = 4
SNOW = 5
LEAVES = 6
WOOD = 7

SEE_THROUGH_BLOCKS = (LEAVES,)  # TODO check why an empty list here renders nothing
MOVE_THROUGH_BLOCKS = (AIR,)

# water
WATER_LINE = 5.6 + CHUNK_SIZE - 8

# terrain levels
SNOW_LVL = 54 + CHUNK_SIZE
STONE_LVL = 49 + CHUNK_SIZE
DIRT_LVL = 40 + CHUNK_SIZE
GRASS_LVL = 8 + CHUNK_SIZE
SAND_LVL = 7 + CHUNK_SIZE

# tree settings
TREE_PROBABILITY = 0.02
TREE_WIDTH, TREE_HEIGHT = 4, 8
TREE_H_WIDTH, TREE_H_HEIGHT = TREE_WIDTH // 2, TREE_HEIGHT // 2

# player
PLAYER_SPEED = 0.001
SPEED_LIMIT_FACTOR = 100
PLAYER_ROT_SPEED = 0.007
PLAYER_POS = glm.vec3(CENTER_XZ, WORLD_H * CHUNK_SIZE, CENTER_XZ)
MOUSE_SENSITIVITY = 0.002

HEIGHT_LIMIT = 2 * WORLD_H * CHUNK_SIZE
PLAYER_BUOYANCY = 1.2
PLAYER_JUMP_VEL = PLAYER_SPEED * 4

# PHYSICS
GRAVITY_ACCEL = -0.000006
IN_WATER_ACCEL_FACTOR = 0.1
# wall avoidance distance
AVOIDANCE = 3 * NEAR
