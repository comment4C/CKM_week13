from numpy import array, ndarray, zeros, dot, cross, float32, identity
from numpy.linalg import norm
from math import sqrt, sin, cos, tan, acos, pi


def Identity():
    return array(((1, 0, 0, 0),
                  (0, 1, 0, 0),
                  (0, 0, 1, 0),
                  (0, 0, 0, 1)), dtype=float32)

def normalize(v):
    l = norm(v)
    if l == 0:
        return v
    else:
        return v/l

def Translate(tx, ty, tz):
    # Fix me!
    return array(((1, 0, 0, tx),
                  (0, 1, 0, ty),
                  (0, 0, 1, tz),
                  (0, 0, 0, 1)), dtype=float32)

def Scale(sx, sy, sz):
    # Fix me!
    return array(((sx, 0, 0, 0),
                  (0, sy, 0, 0),
                  (0, 0, sz, 0),
                  (0, 0, 0, 1)), dtype=float32)

def Rotate(angle, x, y, z):
    # Fix me!
    c = cos(angle)
    s = sin(angle)
    return array(( (pow(x, 2)*(1-c) + c, (x*y)*(1-c) - (z*s), (x*z)*(1-c) + (y*s), 0),
                   ((y*x)*(1-c) + (z*s), pow(y, 2)*(1-c) + c, (y*z)*(1-c) - (x*s), 0),
                   ((z*x)*(1-c) - (y*s), (z*y)*(1-c) + (x*s), pow(z, 2)*(1-c) + c, 0),
                   (0, 0, 0, 1)), dtype=float32)

def LookAt(eyex, eyey, eyez, atx, aty, atz, upx, upy, upz):
    # Fix me!
    eye = array((eyex, eyey, eyez))
    at = array((atx, aty, atz))
    up = array((upx, upy, upz))
    Z = normalize(eye-at)
    Y = normalize(up)
    X = normalize(cross(Y,Z))
    Y = normalize(cross(Z,X))
    return array(((X[0], X[1], X[2], (-1)*dot(X, eye)),
                  (Y[0], Y[1], Y[2], (-1)*dot(Y, eye)),
                  (Z[0], Z[1], Z[2], (-1)*dot(Z, eye)),
                  (0, 0, 0, 1)), dtype=float32)


def Perspective(fovy, aspect, zNear, zFar):
    # Fix me!
    return array(((1/(tan(fovy*pi/180/2)*aspect), 0, 0, 0),
                  (0, 1/(tan(fovy*pi/180/2)), 0, 0),
                  (0, 0, (-1)*(zFar + zNear)/(zFar - zNear), (-2*zNear*zFar)/(zFar - zNear)),
                  (0, 0, -1, 0)), dtype=float32)

def Frustum(left, right, bottom, top, near, far):
    # Fix me!
    return array((((2*near)/(right-left), 0, (right+left)/(right-left), 0),
                  (0, (2*near)/(top-bottom), (top+bottom)/(top-bottom), 0),
                  (0, 0, (-1)*((far+near)/(far-near)), (-1)*((2*far*near)/(far-near))),
                  (0, 0, -1, 0)), dtype=float32)

def Ortho(left, right, bottom, top, near, far):
    # Fix me!
    return array(((2/(right-left), 0, 0, (-1)*((right+left)/(right-left))   ),
                  (0, 2/(top-bottom), 0, (-1)*((top+bottom)/(top-bottom))   ),
                  (0, 0, -2/(far-near),  (-1)*((far+near)/(far-near))       ),
                  (0, 0, 0, 1)), dtype=float32)