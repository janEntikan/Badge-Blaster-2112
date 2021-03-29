"""
A place for various utility functions/classes...
If it doesn't fit elsewhere, plonk it in here!
"""

from random import uniform


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
