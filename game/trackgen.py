"""
Generator for the racetrack and surrounding decoration.
"""

from math import ceil, floor
from typing import Dict, List

from panda3d import core

from . import util
from .common import TG_CHUNK_TRIGGER, TG_MAX_ROAD_X, TG_MAX_SKEW_PER_UNIT, TG_UNITS_PER_CHUNK


class TrackGenerator:
    pass


class DummyTrackGenerator(TrackGenerator):
    def __init__(self, spawn_callback):
        self._difficulty = 0.1
        self._car_position = None
        self._spawn_callback = spawn_callback
        self._track = []
        self._width = []
        self._y_offset = 0

    def update(self, car_position):
        self._car_position = car_position
        if car_position.y + TG_CHUNK_TRIGGER > len(self._track) + self._y_offset:
            self._add_chunks()

    def query(self, y):
        """Returns left and right border x at given y pos as tuple."""
        cl, fl = ceil(y - 1 - self._y_offset), floor(y - 1 - self._y_offset)
        fr = y - floor(y)
        x = self._track[fl] * fr + self._track[cl] * (1.0 - fr)
        w = self._width[fl] * fr + self._width[cl] * (1.0 - fr)
        return x - w, x + w

    def _add_chunks(self):
        start = 0 if len(self._track) == 0 else self._track[-1]
        self._track += util.noise1D(TG_UNITS_PER_CHUNK,
            (-TG_MAX_ROAD_X, TG_MAX_ROAD_X), TG_MAX_SKEW_PER_UNIT * self._difficulty, start)
        self._width += [TG_MAX_ROAD_X * 0.1] * TG_UNITS_PER_CHUNK
        if len(self._track) > TG_UNITS_PER_CHUNK:
            self._track = self._track[TG_UNITS_PER_CHUNK:]
            self._width = self._width[TG_UNITS_PER_CHUNK:]
            self._y_offset += TG_UNITS_PER_CHUNK

    def set_difficulty(self, difficulty):
        self._difficulty = difficulty
