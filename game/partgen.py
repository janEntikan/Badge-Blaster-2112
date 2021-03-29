"""Provides a function to skew and scale a track part."""

from panda3d import core

from . import preprocess as pp


def _process_vert(v, bounds, hskew, scale_start, scale_end):
    v = core.Vec3(v)
    flen = 2 * bounds.hlen
    f = (flen - (bounds.bmax.y - v.y)) / flen
    scale = (scale_end - scale_start) * f + scale_start
    v.x = v.x * scale
    if v.y < 0:
        hskew = -hskew
        f = (v.y) / bounds.hlen
    elif v.y == 0:
        return v
    f = abs(v.y / bounds.hlen)
    v.x = v.x + hskew * f
    return v


def _write_vertex_data(vdata, bounds, hskew, scale_start, scale_end):
    vwrite = core.GeomVertexWriter(vdata, 'vertex')
    vread = core.GeomVertexReader(vdata, 'vertex')
    while not vread.is_at_end():
        v = vread.get_data3()
        vwrite.set_data3(_process_vert(v, bounds, hskew, scale_start, scale_end))


def generate_part(model, bounds, hskew, scale_start, scale_end):
    np = core.NodePath('track part')
    model.copy_to(np)
    for n in pp.geom_node_gen(np):
        for geom in pp.geom_gen(n, True):
            vdata = geom.modify_vertex_data()
            _write_vertex_data(vdata, bounds, hskew, scale_start, scale_end)
    return np
