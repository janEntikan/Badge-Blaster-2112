"""
Pre-processing module to map the indeces of vertices to their relative y
position for faster vertex manipulation at runtime.
"""

from dataclasses import dataclass, field

from panda3d import core


@dataclass
class Bounds:
    bmax:core.Vec3 = field(default_factory=core.Vec3)
    bmin:core.Vec3 = field(default_factory=core.Vec3)
    hlen:float = 0
    width:float = 0
    depth:float = 0

    def __post_init_(self):
        inf = float('inf')
        self.bmax.set(-inf, -inf, -inf)
        self.bmin.set(inf, inf, inf)

    def finalize(self):
        self.width = self.bmax.x - self.bmin.x
        self.hlen = (self.bmax.y - self.bmin.y) / 2
        self.depth = abs(self.bmin.z)


def _process_geom(geom, bounds):
    vdata = geom.get_vertex_data()
    vertex = core.GeomVertexReader(vdata, 'vertex')

    while not vertex.is_at_end():
        v = vertex.get_data3()
        bounds.bmax.x = max(bounds.bmax.x, v.x)
        bounds.bmax.y = max(bounds.bmax.y, v.y)
        bounds.bmax.z = max(bounds.bmax.z, v.z)
        bounds.bmin.x = min(bounds.bmin.x, v.x)
        bounds.bmin.y = min(bounds.bmin.y, v.y)
        bounds.bmin.z = min(bounds.bmin.z, v.z)


def geom_gen(geom_node, modify=False):
    for i in range(geom_node.get_num_geoms()):
        if modify:
            yield geom_node.modify_geom(i)
        else:
            yield geom_node.get_geom(i)


def geom_node_gen(model):
    geom_nodes = model.find_all_matches('**/+GeomNode')
    for np in geom_nodes:
        yield np.node()


def get_model_bounds(model):
    bounds = Bounds()
    for n in geom_node_gen(model):
        for geom in geom_gen(n):
            _process_geom(geom, bounds)
    bounds.finalize()
    return bounds


class PreProcessor:
    def __init__(self, models):
        self._models = {}

    def _process_model(self, model):
        pass

    def __getitem__(self, item):
        pass

