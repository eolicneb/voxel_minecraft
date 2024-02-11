from settings import glm


def invert_triangle(p0, p1, p2):
    return p0, p2, p1


def invert_triangles(*triangles):
    for triangle in zip(triangles[::3], triangles[1::3], triangles[2::3]):
        for p in invert_triangle(*triangle):
            yield p


def reflex(points, normal, point_through=None):
    dim = len(normal)
    disp = {2: glm.vec2, 3: glm.vec3}
    vec = disp[dim]
    point_through = point_through or vec()
    points = (vec(p) for p in points)
    normal = glm.normalize(normal)
    Q = 2 * glm.dot(point_through, normal) * normal
    for point in points:
        yield tuple(Q + point - 2 * glm.dot(point, normal) * normal)
