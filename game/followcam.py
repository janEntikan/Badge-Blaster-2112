"""Lerped camera to lazily follow the player on the x axis."""

from direct.showbase.DirectObject import DirectObject

from .common import FC_MAX_SPEED, FC_EXP


class FollowCam(DirectObject):
    def __init__(self, maxspeed=5.0):
        self.window_width = 0
        self.on_window_evt(None)
        self.accept(base.win.get_window_event(), self.on_window_evt)

    def update(self, dt):
        delta = base.player.root.get_x() - base.camx
        speed = (abs(delta) / self.window_width) ** FC_EXP
        base.camx += delta * speed * FC_MAX_SPEED * dt

    def on_window_evt(self, window):
        x = base.win.get_properties().get_x_size()
        y = base.win.get_properties().get_y_size()
        self.window_width = x / min(x, y)
