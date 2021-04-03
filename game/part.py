"""
In charge of indexing and preprocessing road parts.
"""

from dataclasses import dataclass, field
from hashlib import sha384

from panda3d import core
from direct.stdpy.file import *
from direct.stdpy import pickle

from .common import PR_DEFAULT_DENSITY
from . import preprocess as pp
from . import util


def chk_timestamp(key, base_type):
    h = sha384(f'{key}-{base_type}'.encode()).hexdigest()
    lvl_fname = core.Filename(f'assets/cache/{h}')
    bam_fname = core.Filename(f'assets/models/{key}.bam')
    timestamp = 0
    need_reload = True
    if lvl_fname.exists():
        with open(lvl_fname.to_os_specific(), 'r') as f:
            try:
                timestamp = int(f.read())
            except ValueError:
                pass
    else:
        lvl_fname.make_dir()
        need_reload = True
    bts = bam_fname.get_timestamp()
    if bts == timestamp:
        need_reload = False
    with open(lvl_fname.to_os_specific(), 'w') as f:
        f.write(str(bts))
    return need_reload, lvl_fname


def get_bounds(need_reload, key, np):
    h = sha384(f'{key}-road-{np.name}'.encode()).hexdigest()
    fname = core.Filename(f'assets/cache/{h}')
    if need_reload:
        bounds = pp.get_model_bounds(np)
        with open(fname.to_os_specific(), 'wb') as f:
            pickle.dump(bounds, f)
    else:
        with open(fname.to_os_specific(), 'rb') as f:
            bounds = pickle.load(f)
    return bounds


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
            need_reload, lvl_fname = chk_timestamp(key, 'road')
            if key not in self._parts:
                self._parts[key] = {}
            if 'road' not in self._parts[key]:
                self._parts[key]['road'] = []
            for np in model.find_all_matches('**/road_part*'):
                np.detach_node()
                util.set_faux_lights(np)
                np.clear_transform()
                bounds = get_bounds(need_reload, key, np)
                part = Part(key, np.name, np, bounds)
                if 'transition' in np.name:
                    self._parts[key]['transition'] = part
                else:
                    self._parts[key]['road'].append(part)
                np.flatten_strong()
            self._compute_ground(key)

    def _scan_props(self, models):
        for key, model in models.items():
            need_reload, lvl_fname = chk_timestamp(key, 'props')
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
                    bounds = get_bounds(need_reload, key, child)
                    part = Part(key, child.name, child, bounds, d)

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

    def store(self, fpath):
        pass

    def load(self, fpath):
        pass

    def __getitem__(self, item):
        return self._parts[item[0]][item[1]]
