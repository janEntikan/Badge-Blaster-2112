"""
Generator for the racetrack and surrounding decoration.
"""

from math import ceil, floor
import random
from typing import Dict, List

from panda3d import core

from . import util
from . import part
from . import partgen
from .common import (TG_CHUNK_TRIGGER, TG_MAX_ROAD_X, TG_MAX_SKEW_PER_UNIT,
                     TG_UNITS_PER_CHUNK, TG_MIN_SPAWN_DIST, TG_MAX_SPAWN_DIST,
                     TG_WIDTHS, TG_VISIBLE)

UNIT = 10
UNIT_MULT = 1 / 10


class TrackGenerator:
    def __init__(self):
        self._difficulty = 0.1
        self._car_position = None
        self._spawn_callback = None
        self._track = []
        self._next_part_y = 0
        self._ymax = 0
        self._parts = []
        self._width = []
        self._y_offset = 0
        self._next_spawn = 1
        self._next_variant = 30
        self._variant = 1
        self._part_mgr:part.PartMgr = base.part_mgr
        self.update(core.Vec3(0))

    def update(self, car_position):
        self._car_position = car_position
        while car_position.y + TG_CHUNK_TRIGGER >= len(self._track) * UNIT + self._y_offset:
            self._add_chunks()
        if car_position.y >= self._next_spawn:
            self._spawn_enemy()
        while self._add_track_part():
            pass

    def query(self, y):
        """Returns left and right border x at given y pos as tuple."""
        x, w = self._qry_center_w(y)
        return x - w, x + w

    def _qry_center_w(self, y):
        if y < self._y_offset:
            return 0, 0
        while y > self._y_offset + len(self._track) * UNIT:
            # FIXME: If time permits, solve more elegant...
            self._add_chunks(False)
        ynorm = max((y - self._y_offset) * UNIT_MULT - 1, 0)
        cl, fl = ceil(ynorm), floor(ynorm)
        fr = y * UNIT_MULT - floor(y * UNIT_MULT)
        x = self._track[cl] * fr + self._track[fl] * (1.0 - fr)
        w = self._width[cl] * fr + self._width[fl] * (1.0 - fr)
        return x, w

    def register_spawn_callback(self, spawn_callback):
        self._spawn_callback = spawn_callback

    def set_difficulty(self, difficulty):
        self._difficulty = difficulty

    def _add_chunks(self, drop=True):
        start = 0 if len(self._track) == 0 else self._track[-1]
        num = ceil(TG_UNITS_PER_CHUNK * UNIT_MULT)
        self._track += util.generate_track_offset(num, (-TG_MAX_ROAD_X, TG_MAX_ROAD_X),
            self._difficulty, start)
        self._width += util.generate_width(num, TG_WIDTHS, self._width[-1] if self._width else TG_WIDTHS[-1])
        self._ymax += TG_UNITS_PER_CHUNK
        if drop and len(self._track) > num * 2:
            self._track = self._track[num:]
            self._width = self._width[num:]
            self._y_offset += TG_UNITS_PER_CHUNK
            while True:
                if self._parts[0].get_y() < self._y_offset:
                    self._parts[0].detach_node()
                    self._parts.pop(0)
                    continue
                break

    def _add_track_part(self):
        part = self._select_part()
        hlen = part.bounds.hlen
        new_next = self._next_part_y + hlen * 2
        if new_next <= self._car_position.y + TG_VISIBLE:
            start = self._qry_center_w(self._next_part_y)
            end = self._qry_center_w(new_next)
            if not start or not end:
                raise ValueError('Unable to query while adding a part')
            start_x, start_w, end_x, end_w = start + end
            hskew = (end_x - start_x) / 2
            scale_start = (start_w * 2) / part.bounds.width
            scale_end = (end_w * 2) / part.bounds.width
            np = partgen.generate_part(part.model, part.bounds, hskew, scale_start, scale_end)
            np.reparent_to(base.render)
            self._parts.append(np)
            x = (end_x - start_x) / 2 + start_x
            np.set_pos(x, self._next_part_y, 0)
            self._next_part_y = new_next
            return True
        return False

    def _select_part(self):
        # FIXME: actually do sensible selection
        self._next_variant -= 1
        if self._next_variant == 0:
            self._variant = random.randint(0, 3)
            self._next_variant = random.randint(15, 50)
        return self._part_mgr.get_road_part('forest', self._variant)

    def _spawn_enemy(self):
        # FIXME: make spawning better
        enemy_y = random.uniform(TG_MIN_SPAWN_DIST, TG_MAX_SPAWN_DIST)
        self._next_spawn += enemy_y * (4 - self._difficulty)
        enemy_y += self._car_position.y
        left, right = self.query(enemy_y)
        offset = (right - left) * 0.1
        enemy_x = random.uniform(left + offset, right - offset)
        if self._spawn_callback:
            self._spawn_callback(core.Point3(enemy_x, enemy_y, 0))
