"""
In charge of indexing and preprocessing road parts.
"""

from dataclasses import dataclass, field

from panda3d import core

from .common import PR_DEFAULT_DENSITY
from . import preprocess as pp
from . import util


@dataclass
class Part:
    level_type:str
    part_type:str
    model:core.NodePath
    bounds:pp.Bounds
    density:float = -1.0


class PartMgr:
    def __init__(self, models, keys=('test', )):
        self._parts = {}
        self._build_lib(models, keys)

    def _build_lib(self, models, keys):
        for k in keys:
            if k == 'parts':
                self._scan_road_parts(models)
            elif k == 'props':
                self._scan_props(models)
            else:
                print(f'Unknown key "{k}"')

    def _compute_ground(self, key):
        ground = float('inf')
        for part in self._parts[key]['road']:
            ground = min(ground, part.bounds.depth)
        self._parts[key]['ground'] = ground

    def _scan_road_parts(self, models):
        for key, model in models.items():
            if key not in self._parts:
                self._parts[key] = {}
            if 'road' not in self._parts[key]:
                self._parts[key]['road'] = []
            for np in model.find_all_matches('**/road_part*'):
                np.detach_node()
                util.set_faux_lights(np)
                np.clear_transform()
                part = Part(key, np.name, np, pp.get_model_bounds(np))
                if 'transition' in np.name:
                    self._parts[key]['transition'] = part
                else:
                    self._parts[key]['road'].append(part)
                np.flatten_strong()
            self._compute_ground(key)

    def _scan_props(self, models):
        for key, model in models.items():
            if key not in self._parts:
                self._parts[key] = {}
            if 'props' not in self._parts[key]:
                self._parts[key]['props'] = []
            for np in model.find_all_matches('**/props*'):
                np.detach_node()
                np.clear_transform()
                for child in np.get_children():
                    child.detach_node()
                    child.clear_transform()
                    d = child.get_net_tag('density')
                    d = float(d) if d else PR_DEFAULT_DENSITY
                    part = Part(key, child.name, child, pp.get_model_bounds(np), d)

                    lights = []
                    for n in child.find_all_matches('**/*light*'):
                        n.detach_node()
                        lights.append(n)
                    child.flatten_strong()
                    for n in lights:
                        n.reparent_to(child)
                    util.set_faux_lights(child)
                    if part.bounds.width > 0:
                        self._parts[key]['props'].append(part)
                    else:
                        print(f'Could not scan Prop, apparently width is 0: {part}')

    def get_road_part(self, part_type, variant):
        return self._parts[part_type]['road'][variant]

    def get_road_transition(self, part_type):
        return self._parts[part_type]['transition']

    def get_prop(self, part_type, variant):
        return self._parts[part_type]['props'][variant]

    def get_prop_by_density(self, part_type, density_min):
        return [i for i in self._parts[part_type]['props'] if i.density >= density_min]

    def get_prop_by_prefix(self, part_type, prefix):
        return [i for i in self._parts[part_type]['props'] if i.part_type.startswith(f'{prefix}')]

    def get_part_types(self):
        return list(self._parts.keys())

    def num_roads(self, part_type):
        return len(self._parts[part_type]['road'])

    def num_props(self, part_type):
        return len(self._parts[part_type]['props'])

    def ground(self, part_type):
        return self._parts[part_type]['ground']

    def __getitem__(self, item):
        return self._parts[item[0]][item[1]]
