"""
A place for various utility functions/classes...
If it doesn't fit elsewhere, plonk it in here!
"""

from math import sin, pi
from random import uniform, randint, choice

from .common import TG_CURVE_RNG

HPI = pi / 2


def noise1D(num, bounds, max_delta, start=None):
    """
    Noise of `num` values inside `bounds` with `max_delta` between any two
    neighboring points.
    """
    n = [start if start is not None else sum(bounds) / 2]
    while len(n) < num:
        t_bounds = (max(n[-1] - max_delta, bounds[0]),
                    min(n[-1] + max_delta, bounds[1]))
        n.append(uniform(*t_bounds))
    return n


def generate_track_offset(num, bounds, difficulty, start=None):
    """
    Replacement for noise to generate a more sensible track
    """
    n = [start if start is not None else sum(bounds) / 2]
    pc = 1
    while pc < num:
        if num - pc < 4:
            n += [n[-1]] * (num - pc)
            break

        clen = randint(4, num - pc)
        if uniform(*TG_CURVE_RNG) < difficulty:  # Curve
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
