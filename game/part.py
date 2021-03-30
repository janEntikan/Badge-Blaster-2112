"""
In charge of indexing and preprocessing road parts.
"""

from dataclasses import dataclass, field

from panda3d import core

from . import preprocess as pp
from . import util


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
        if keys[0] == 'test':
            part = Part('test', 'styled_road', models['testparts-b'],
                pp.get_model_bounds(models['testparts-b']))
            self._parts['road'] = {'styled_road': [part]}
            return
        for k in keys:
            if k == 'parts':
                self._scan_road_parts(models)
            elif k == 'props':
                self._scan_props(models)
            else:
                print(f'Unknown key "{k}"')

    def _scan_road_parts(self, models):
        for key, model in models.items():
            if 'road' not in self._parts:
                self._parts['road'] = {}
            if key not in self._parts['road']:
                self._parts['road'][key] = []
            for np in model.find_all_matches('**/road_part*'):
                np.detach_node()
                util.set_faux_lights(np)
                np.clear_transform()
                self._parts['road'][key].append(Part(key, key, np, pp.get_model_bounds(np)))

    def _scan_props(self, models):
        pass

    def get_road_part(self, part_type, variant):
        return self._parts['road'][part_type][variant]
