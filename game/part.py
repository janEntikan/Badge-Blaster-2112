"""
In charge of indexing and preprocessing road parts.
"""

from dataclasses import dataclass, field

from panda3d import core

from . import preprocess as pp


@dataclass
class Part:
    level_type:str
    part_type:str
    model:core.NodePath
    bounds:pp.Bounds


class PartMgr:
    def __init__(self, models, keys=('test', )):
        self._parts = {}
        self._build_lib(models, keys)

    def _build_lib(self, models, keys):
        for k in keys:
            if k == 'test':
                part = Part('test', 'styled_road', models['testparts-b'],
                    pp.get_model_bounds(models['testparts-b']))
                self._parts['road'] = {'styled_road': [part]}
                return

        # FIXME: Actually scan models

    def get_road_part(self, part_type, variant):
        return self._parts['road'][part_type][variant]
