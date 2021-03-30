"""Provides a function to skew and scale a track part."""

from panda3d import core


def generate_part(model, bounds, hskew, scale_start, scale_end):
    np = core.NodePath('track part')
    model.copy_to(np)
    np.set_shader(core.Shader.load(core.Shader.SL_GLSL, 'assets/shaders/road.vert', 'assets/shaders/road.frag'))
    np.set_shader_input('i_hskew', hskew)
    np.set_shader_input('i_ymax', bounds.mmax.y)
    np.set_shader_input('i_scale', core.Vec2(scale_start, scale_end))
    np.set_shader_input('i_len', bounds.hlen * 2)
    return np
