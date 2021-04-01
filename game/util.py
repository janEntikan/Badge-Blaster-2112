"""
A place for various utility functions/classes...
If it doesn't fit elsewhere, plonk it in here!
"""

from math import sin, pi
from random import uniform, randint, choice

from panda3d import core

from .common import TG_CURVE_RNG, TG_LOCAL_CURVE_DIV, TG_UNITS_PER_CHUNK, DF_SPLINE_PTS

HPI = pi / 2


def spline_point(t):
    mx = len(DF_SPLINE_PTS) - 1
    p0 = int(t * mx)
    p1 = min(p0 + 1, mx)
    p2 = min(p1 + 1, mx)
    p3 = min(p2 + 1, mx)

    t = t * mx - int(t * mx)
    tt = t * t
    ttt = tt * t

    q1 = -ttt + 2.0 * tt - t
    q2 = 3.0 * ttt - 5.0 * tt + 2.0
    q3 = -3.0 * ttt + 4.0 * tt + t
    q4 = ttt - tt

    ty = 0.5 * (DF_SPLINE_PTS[p0].y * q1 + DF_SPLINE_PTS[p1].y * q2 + DF_SPLINE_PTS[p2].y * q3 + DF_SPLINE_PTS[p3].y * q4)
    return ty


def generate_track_offset(num, bounds, difficulty, start=None, start_straight=False):
    """
    Replacement for noise to generate a more sensible track
    """
    n = [start if start is not None else sum(bounds) / 2]
    if start_straight:
        n += n * 5
    pc = len(n)
    curve_delta = ((max(bounds) - min(bounds)) / TG_LOCAL_CURVE_DIV) * difficulty
    while pc < num:
        if num - pc < 4:
            n += [n[-1]] * (num - pc)
            break

        clen = randint(4, num - pc)
        if uniform(*TG_CURVE_RNG) < difficulty:  # Curve
            cdelta = curve_delta + 1
            while cdelta > curve_delta:
                cdelta = uniform(*bounds) - n[-1]
            n += [sin((i / clen) * HPI) * cdelta + n[-1] for i in range(1, clen + 1)]
        else:
            n += [n[-1]] * clen
        pc += clen
    return n


def generate_width(num, steps, start=None):
    n = [start if start is not None else steps[-1]]
    pc = 1
    while pc < num:
        if num - pc < 4:
            n += [n[-1]] * (num - pc)
            break

        n += [choice(steps)] * randint(4, num - pc)
        pc = len(n)
    return n


def normalize_list(values, bounds=(0, 1)):
    """Normalizes a list of floats in the range of `bounds` in place."""
    vmin, vmax = min(values), max(values)
    bmin, bmax = min(bounds), max(bounds)
    vdelta, bdelta = vmax - vmin, bmax - bmin
    for i in range(len(values)):
        v = values[i]
        v = (v - vmin) / vdelta
        v *= bdelta + bmin
        values[i] = v


def set_faux_lights(node):
    for light in node.find_all_matches('**/*light*'):
        light.set_alpha_scale(0.1)
        light.set_transparency(True)


class AABB:
    def __init__(self, x, y, hw, hh):
        self.x = x
        self.y = y
        self.hw = hw
        self.hh = hh

    def overlap(self, other):
        return (self.inside(other.x - other.hw, other.y - other.hh)
            or self.inside(other.x + other.hw, other.y - other.hh)
            or self.inside(other.x + other.hw, other.y + other.hh)
            or self.inside(other.x - other.hw, other.y + other.hh)
            or other.inside(self.x - self.hw, self.y - self.hh)
            or other.inside(self.x + self.hw, self.y - self.hh)
            or other.inside(self.x + self.hw, self.y + self.hh)
            or other.inside(self.x - self.hw, self.y + self.hh))

    def inside(self, x, y):
        return self.x - self.hw <= x <= self.x + self.hw \
            and self.y - self.hh <= y <= self.y + self.hh
