"""
Generator for the racetrack and surrounding decoration.
"""

from math import ceil, floor, pi
import random
from typing import Dict, List

from panda3d import core

from . import util
from . import part
from .common import *


def generate_part(model, bounds, hskew, scale_start, scale_end, hue):
    np = core.NodePath('track part')
    model.copy_to(np)
    np.set_shader(core.Shader.load(core.Shader.SL_GLSL, 'assets/shaders/road.vert', 'assets/shaders/road.frag'))
    np.set_shader_input('i_hskew', hskew)
    np.set_shader_input('i_ymax', bounds.mmax.y)
    np.set_shader_input('i_scale', core.Vec2(scale_start, scale_end))
    np.set_shader_input('i_len', bounds.hlen * 2)
    np.set_shader_input('i_hue', hue)
    return np


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
        self._next_variant = random.randint(*TG_PART_CHG_RNG)
        self._level = random.choice(['forest', 'desert'])
        self._variant = random.randrange(base.part_mgr.num_roads(self._level))
        self._dense_counter = 0
        self._next_level = random.randint(*TG_LEVEL_CHG_RNG)
        self._level_trans_old = -1
        self._level_trans_new = -1
        self._level_after_trans = ''
        self._level_event_sent = False
        self._current_hue = random.uniform(0, pi)
        self._part_mgr:part.PartMgr = base.part_mgr
        self.update(core.Vec3(0))

    def update(self, car_position):
        self._car_position = car_position
        while car_position.y + TG_CHUNK_TRIGGER >= len(self._track) * TG_UNIT + self._y_offset:
            self._add_chunks()
        if car_position.y >= self._next_spawn:
            self._spawn_enemy()
        while self._add_track_part():
            pass
        while True:
            if self._parts[0].get_y() < car_position.y - TG_DESPAWN:
                self._parts[0].detach_node()
                self._parts.pop(0)
                continue
            break

    def query(self, y):
        """Returns left and right border x at given y pos as tuple."""
        x, w = self._qry_center_w(y)
        return x - w, x + w

    def _qry_center_w(self, y):
        if y < self._y_offset:
            return 0, 0
        while y > self._y_offset + len(self._track) * TG_UNIT:
            # FIXME: If time permits, solve more elegant...
            self._add_chunks(False)
        ynorm = min(max((y - self._y_offset - TG_UNIT) * TG_UNIT_MULT, 0), len(self._track) - 1)
        cl, fl = ceil(ynorm), floor(ynorm)
        fr = y * TG_UNIT_MULT - floor(y * TG_UNIT_MULT)
        x = self._track[cl] * fr + self._track[fl] * (1.0 - fr)
        w = self._width[cl] * fr + self._width[fl] * (1.0 - fr)
        return x, w

    def register_spawn_callback(self, spawn_callback):
        self._spawn_callback = spawn_callback

    def set_difficulty(self, difficulty):
        self._difficulty = difficulty

    def _add_chunks(self, drop=True):
        start = 0 if len(self._track) == 0 else self._track[-1]
        num = ceil(TG_UNITS_PER_CHUNK * TG_UNIT_MULT)
        self._track += util.generate_track_offset(num, (-TG_MAX_ROAD_X, TG_MAX_ROAD_X),
            self._difficulty, start)
        self._width += util.generate_width(num, TG_WIDTHS, self._width[-1] if self._width else TG_WIDTHS[-1])
        self._ymax += TG_UNITS_PER_CHUNK
        if drop and len(self._track) > num * 2:
            self._track = self._track[num:]
            self._width = self._width[num:]
            self._y_offset += TG_UNITS_PER_CHUNK

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
            np = generate_part(part.model, part.bounds, hskew, scale_start, scale_end, self._current_hue)
            np.reparent_to(base.render)
            self._parts.append(np)
            x = (end_x - start_x) / 2 + start_x
            np.set_pos(x, self._next_part_y + TG_UNIT / 2, 0)
            scale = (scale_start + scale_end) / 2
            self._populate_props(part.bounds.depth,
                (part.bounds.rmin.x - part.bounds.mmin.x) * scale,
                (part.bounds.mmax.x - part.bounds.rmax.x) * scale)
            self._next_part_y = new_next
            return True
        return False

    def _select_part(self):
        # FIXME: actually do sensible selection
        self._next_variant -= 1
        if self._next_variant <= 0:
            if self._next_level > 0:                                    # Change Variant
                self._variant = random.randrange(self._part_mgr.num_roads(self._level))
                self._next_variant = random.randint(*TG_PART_CHG_RNG)
                self._next_level -= 1
            elif self._level_trans_new == self._level_trans_old == -2:  # Setup transition
                self._level_trans_old = random.randint(*TG_TRANS_RNG) - 1
                self._level_trans_new = random.randint(*TG_TRANS_RNG)
                self._level_after_trans = self._level
                while self._level_after_trans == self._level:
                    self._level_after_trans = random.choice(base.levels)
                return self._part_mgr.get_road_transition(self._level)
            elif self._level_trans_old > 0:                             # Transition part old
                self._level_trans_old -= 1
                self._level_trans_old = -1 if self._level_trans_old <= 0 else self._level_trans_old
                return self._part_mgr.get_road_transition(self._level)
            elif self._level_trans_new > 0:                             # Transition part new
                if not self._level_event_sent:
                    messenger.send('level-transition', [self._level_after_trans])
                    self._current_hue = random.uniform(0, pi)
                    self._level_event_sent = True
                self._level = self._level_after_trans
                self._level_trans_new -= 1
                self._level_trans_new = -1 if self._level_trans_new <= 0 else self._level_trans_new
                return self._part_mgr.get_road_transition(self._level_after_trans)
            else:                                                       # Actual level change
                self._variant = random.randrange(self._part_mgr.num_roads(self._level))
                self._next_variant = random.randint(*TG_PART_CHG_RNG)
                self._next_level = random.randint(*TG_LEVEL_CHG_RNG)
                self._level_trans_new = -2
                self._level_trans_old = -2
                self._level_event_sent = False
        return self._part_mgr.get_road_part(self._level, self._variant)

    def _populate_props(self, z, bl, br):
        l, r = self.query(self._next_part_y)
        self._place_dense(l - bl / 2, r + br / 2)
        self._place_decoration(z, bl, br)

    def _place_decoration(self, z, bl, br):
        remaining = random.randint(*PR_ATTEMPTS)
        placed = []
        while remaining:
            part = random.choice(self._part_mgr[(self._level, 'props')])
            if part.density == 1:
                continue
            chk = PR_DEFAULT_DENSITY if part.density < 0 else part.density
            remaining -= 1
            if random.random() > chk:
                continue
            np = core.NodePath('prop')
            part.model.copy_to(np)
            np.reparent_to(base.render)
            fail = PR_PLACE_ATTEMPTS
            while fail > 0:
                y = self._next_part_y + random.uniform(0, TG_UNIT)
                x, w = self._qry_center_w(y)
                dist = int(part.part_type[0])
                if dist == 4:  # FIXME: Handle underneath the road placement
                    pass
                elif dist == 5:
                    dist = random.randint(1, 3)
                dist = (dist - 1) * PR_OFFSET
                if random.random() < 0.5:
                    angle = 0
                    x = x - w - dist - bl
                else:
                    angle = 180
                    x = x + w + dist + br
                hw = (part.bounds.width / 2) * PR_SCALE
                hh = part.bounds.hlen
                mbb = util.AABB(x + part.bounds.mmin.x + hw, y + part.bounds.mmin.y + hh, hw, hh)
                can_place = True
                for bb in placed:
                    if bb.overlap(mbb):
                        can_place = False
                        fail -= 1
                        break
                if can_place:
                    np.set_pos(x, y, z)
                    np.set_scale(PR_SCALE)
                    np.set_h(angle)
                    placed.append(mbb)
                    self._parts.append(np)
                    break

    def _place_dense(self, left, right):
        # FIXME: Account for possibly more than two prop with 100% density
        for i, part in enumerate(self._part_mgr.get_prop_by_density(self._level, 1)):
            np = core.NodePath('prop')
            part.model.copy_to(np)
            np.reparent_to(base.render)

            if (self._dense_counter + i) % 2:
                np.set_scale(PR_SCALE)
                np.set_pos(left, self._next_part_y, 0)
            else:
                np.set_h(180)
                np.set_scale(PR_SCALE)
                np.set_pos(right, self._next_part_y, 0)

            self._parts.append(np)
        self._dense_counter += 1

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
