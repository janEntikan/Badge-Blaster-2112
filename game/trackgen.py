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


ROAD_SHADER = core.Shader.load(core.Shader.SL_GLSL, 'assets/shaders/road.vert', 'assets/shaders/road.frag')
PROP_SHADER = core.Shader.load(core.Shader.SL_GLSL, 'assets/shaders/prop.vert', 'assets/shaders/prop.frag')
LIGHT_SHADER = core.Shader.load(core.Shader.SL_GLSL, 'assets/shaders/light.vert', 'assets/shaders/light.frag')


def generate_part(model, bounds, hskew, scale_start, scale_end, hue):
    np = core.NodePath('track part')
    model.copy_to(np)
    np.set_shader(ROAD_SHADER)
    np.set_shader_input('i_hskew', hskew)
    np.set_shader_input('i_ymax', bounds.mmax.y)
    np.set_shader_input('i_scale', core.Vec2(scale_start, scale_end))
    np.set_shader_input('i_len', bounds.hlen * 2)
    np.set_shader_input('i_hue', hue)
    np.set_shader_input('i_zmax', bounds.mmax.z)
    np.set_shader_input('i_height', bounds.mmax.z - bounds.mmin.z)
    np.set_shader_input('i_shade', SH_Z_SHADE_COLOR)
    np.set_shader_input('i_shade_exp', SH_Z_SHADE_EXP)
    return np


class TrackGenerator:
    def __init__(self):
        self._car_position = None
        self._spawn_callback = None
        self._track = []
        self._parts = []
        self._width = []
        self._levels = []
        self.reset()

    def reset(self):
        self._levels = list(base.levels)
        random.shuffle(self._levels)
        print("Level sequence", self._levels)
        self._level = self._levels.pop(0)
        self._next_variant = random.randint(*TG_PART_CHG_RNG)
        self._variant = random.randrange(base.part_mgr.num_roads(self._level))
        #self._next_level = random.randint(*TG_LEVEL_CHG_RNG)
        self._next_level = -1
        self._next_variant = -1
        self._difficulty = 0.1
        self._next_spawn = 1
        self._next_part_y = 0
        self._y_offset = 0
        self._ymax = 0
        self._level_trans_old = -2
        self._level_trans_new = -2
        self._level_after_trans = ''
        self._y_trans_start = -1
        self._y_trans_end = -1
        self._level_event_sent = False
        self._current_hue = 0
        self._next_hue = self._current_hue
        self._part_mgr:part.PartMgr = base.part_mgr
        self._first_piece = True
        self._no_props = 0
        self._dense_counter = 0
        self._aabb = []

        while self._parts:
            self._parts.pop().remove_node()
        self._track.clear()
        self._width.clear()

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
        if len(self._aabb) > TG_MIN_AABB * 2:
            self._aabb = self._aabb[TG_MIN_AABB:]
            print(f'Dropped {TG_MIN_AABB} AABB instances')

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
            self._difficulty, start, len(self._track) == 0)
        self._width += util.generate_width(num, TG_WIDTHS, self._width[-1] if self._width else TG_WIDTHS[-1])
        self._ymax += TG_UNITS_PER_CHUNK
        if drop and len(self._track) > num * 2:
            self._track = self._track[num:]
            self._width = self._width[num:]
            self._y_offset += TG_UNITS_PER_CHUNK

    def _add_track_part(self):
        new_next = self._next_part_y + TG_UNIT
        if hasattr(base, 'player'):
            tilt = 1 + base.player.cam_tilt
        else:
            tilt = 1
        if new_next <= self._car_position.y + TG_VISIBLE * tilt:
            part = self._select_part()
            self._next_variant -= 1
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
            if self._first_piece:
                self._first_piece = False
                np = generate_part(part.model, part.bounds, hskew, scale_start, scale_start, self._current_hue)
                np.reparent_to(base.render)
                self._parts.append(np)
                np.set_pos(start_x, self._next_part_y - TG_UNIT / 2, 0)
            elif self._no_props <= 0 and self._level_trans_new == self._level_trans_old == -2:
                scale = (scale_start + scale_end) / 2
                self._populate_props(part.bounds.depth,
                    (part.bounds.rmin.x - part.bounds.mmin.x) * scale,
                    (part.bounds.mmax.x - part.bounds.rmax.x) * scale)
            self._no_props -= 1
            self._next_part_y = new_next
            return True
        return False

    def _select_part(self):
        # FIXME: actually do sensible selection
        if self._next_variant <= 0:
            if self._next_level > 0:                                    # Change Variant
                self._variant = random.randrange(self._part_mgr.num_roads(self._level))
                self._next_variant = random.randint(*TG_PART_CHG_RNG)
                self._next_level -= 1
            elif self._level_trans_new == self._level_trans_old == -2:  # Setup transition
                self._level_trans_old = random.randint(*TG_TRANS_RNG) - 1
                self._level_trans_new = random.randint(*TG_TRANS_RNG)
                self._y_trans_start = self._next_part_y - TG_UNIT
                self._y_trans_end = self._next_part_y + (self._level_trans_new + self._level_trans_old + 1) * TG_UNIT
                self._level_after_trans = self._level
                while self._level_after_trans == self._level:
                    if self._levels:
                        self._level_after_trans = self._levels.pop(0)
                    else:
                        self._levels = list(base.levels)
                        random.shuffle(self._levels)
                        print("Shuffled new level sequence:", self._levels)
                        self._level_after_trans = self._levels.pop(0)
                return self._part_mgr.get_road_transition(self._level)
            elif self._level_trans_old > 0:                             # Transition part old
                self._level_trans_old -= 1
                self._level_trans_old = -1 if self._level_trans_old <= 0 else self._level_trans_old
                return self._part_mgr.get_road_transition(self._level)
            elif self._level_trans_new > 0:                             # Transition part new
                if not self._level_event_sent:
                    messenger.send('level-transition', [self._level_after_trans])
                    self._current_hue = self._next_hue
                    self._next_hue = random.uniform(0, pi) if base.level_counter > 3 else 0
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
        ground = self._part_mgr.ground(self._level)
        remaining = random.randint(*PR_ATTEMPTS)
        while remaining:
            part = random.choice(self._part_mgr[(self._level, 'props')])
            dist = int(part.part_type[0])
            if dist == 0:
                continue
            remaining -= 1
            if random.random() > part.density:
                continue
            np = core.NodePath('prop')
            part.model.copy_to(np)

            fail = PR_PLACE_ATTEMPTS
            while fail > 0:
                y = self._next_part_y + random.uniform(TG_UNIT, TG_UNIT * 2)
                x, w = self._qry_center_w(y)
                if w == 0:
                    fail -= 1
                    continue
                sdist = dist
                if dist == 4:  # Underneath!!
                    x = x
                    z = ground
                    angle = 0
                else:
                    if dist == 1:
                        z = 0
                    else:
                        z = ground
                    if dist == 5:
                        dist = random.randint(1, 3)

                    dist = (dist - 1) * PR_OFFSET + (dist - 1) * (part.bounds.mmax.x * PR_SCALE)
                    if random.random() < 0.5:
                        angle = 0
                        x = x - w - dist - bl
                    else:
                        angle = 180
                        x = x + w + dist + br

                if angle == 0:
                    mbb = util.AABB(
                        x + part.bounds.mmin.x * PR_SCALE,
                        x + part.bounds.mmax.x * PR_SCALE,
                        y + part.bounds.mmin.y * PR_SCALE,
                        y + part.bounds.mmax.y * PR_SCALE
                    )
                else:
                    mbb = util.AABB(
                        x + part.bounds.mmax.x * PR_SCALE,
                        x + part.bounds.mmin.x * PR_SCALE,
                        y + part.bounds.mmin.y * PR_SCALE,
                        y + part.bounds.mmax.y * PR_SCALE
                    )
                can_place = True
                for bb in self._aabb:
                    if bb.overlap(mbb):
                        can_place = False
                        fail -= 1
                        dist = sdist
                        break
                if can_place:
                    np.reparent_to(base.render)
                    np.set_shader(PROP_SHADER)
                    np.set_shader_input('i_hue', self._current_hue)
                    np.set_shader_input('i_zmax', part.bounds.mmax.z)
                    np.set_shader_input('i_height', part.bounds.mmax.z - part.bounds.mmin.z)
                    np.set_shader_input('i_shade', SH_Z_SHADE_COLOR)
                    np.set_shader_input('i_shade_exp', SH_Z_SHADE_EXP)
                    np.set_shader_input('i_alpha_f', 1.0)
                    np.set_pos(x, y, z)
                    np.set_scale(PR_SCALE)
                    np.set_h(angle)
                    self._aabb.append(mbb)
                    self._parts.append(np)
                    break

    def _place_dense(self, left, right):
        # FIXME: Account for possibly more than two prop with 100% density
        placed = 0
        dense_parts = self._part_mgr.get_prop_by_prefix(self._level, 0)
        random.shuffle(dense_parts)
        for part in dense_parts:
            if placed > 1:
                break
            if random.random() > part.density:
                continue
            np = core.NodePath('prop')
            part.model.copy_to(np)
            np.reparent_to(base.render)
            np.set_shader(PROP_SHADER)
            np.set_shader_input('i_hue', self._current_hue)
            np.set_shader_input('i_zmax', part.bounds.mmax.z)
            np.set_shader_input('i_height', part.bounds.mmax.z - part.bounds.mmin.z)
            np.set_shader_input('i_shade', SH_Z_SHADE_COLOR)
            np.set_shader_input('i_shade_exp', SH_Z_SHADE_EXP)
            np.set_shader_input('i_alpha_f', 1.0)

            for n in np.get_children():
                bmin, bmax = np.get_tight_bounds()
                origin = Vec3(
                    (bmax.x - bmin.x) / 2 + bmin.x,
                    (bmax.y - bmin.y) / 2 + bmin.y,
                    bmax.z,
                )
                end = Vec3(
                    (bmax.x - bmin.x) / 2 + bmin.x,
                    (bmax.y - bmin.y) / 2 + bmin.y,
                    bmin.z,
                )
                n.set_shader(LIGHT_SHADER)
                n.set_shader_input('i_hue', self._current_hue)
                n.set_shader_input('i_end', end)
                n.set_shader_input('i_origin', origin)
                n.set_shader_input('i_shade', SH_Z_SHADE_COLOR)
                n.set_shader_input('i_shade_exp', SH_Z_SHADE_EXP)
                n.set_shader_input('i_alpha_f', 0.1)

            if (self._dense_counter + placed) % 2:
                np.set_scale(PR_SCALE)
                np.set_pos(left, self._next_part_y, 0)
            else:
                np.set_h(180)
                np.set_scale(PR_SCALE)
                np.set_pos(right, self._next_part_y, 0)

            self._parts.append(np)
            placed += 1

        self._dense_counter += 1

    def _spawn_enemy(self):
        # FIXME: make spawning better
        tilt = 1 + base.player.cam_tilt
        enemy_y = random.uniform(TG_MIN_SPAWN_DIST * tilt, TG_MAX_SPAWN_DIST * tilt)
        self._next_spawn += enemy_y * (4 - self._difficulty)
        enemy_y += self._car_position.y
        if self._y_trans_start <= enemy_y <= self._y_trans_end:
            return
        left, right = self.query(enemy_y)
        if self._spawn_callback:
            self._spawn_callback(enemy_y, left, right)
