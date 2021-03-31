"""
Pre-processing module to map the indeces of vertices to their relative y
position for faster vertex manipulation at runtime.
"""

from dataclasses import dataclass, field

from panda3d import core


@dataclass
class Bounds:
    mmax:core.Vec3 = field(default_factory=core.Vec3)
    mmin:core.Vec3 = field(default_factory=core.Vec3)
    rmax:core.Vec3 = field(default_factory=core.Vec3)
    rmin:core.Vec3 = field(default_factory=core.Vec3)
    hlen:float = 0
    width:float = 0
    depth:float = 0

    def __post_init_(self):
        inf = float('inf')
        self.mmax.set(-inf, -inf, -inf)
        self.mmin.set(inf, inf, inf)
        self.rmax.set(-inf, -inf, -inf)
        self.rmin.set(inf, inf, inf)

    def finalize(self):
        self.width = self.rmax.x - self.rmin.x
        if self.width == 0:
            self.width = self.mmax.x - self.mmin.x
        self.hlen = (self.rmax.y - self.rmin.y) / 2
        if self.hlen == 0:
            self.hlen = (self.mmax.y - self.mmin.y) / 2
        self.depth = abs(self.mmin.z)


def _process_geom(geom, bounds, is_road):
    vdata = geom.get_vertex_data()
    vertex = core.GeomVertexReader(vdata, 'vertex')

    while not vertex.is_at_end():
        v = vertex.get_data3()
        bounds.mmax.x = max(bounds.mmax.x, v.x)
        bounds.mmax.y = max(bounds.mmax.y, v.y)
        bounds.mmax.z = max(bounds.mmax.z, v.z)
        bounds.mmin.x = min(bounds.mmin.x, v.x)
        bounds.mmin.y = min(bounds.mmin.y, v.y)
        bounds.mmin.z = min(bounds.mmin.z, v.z)
        if is_road:
            bounds.rmax.x = max(bounds.rmax.x, v.x)
            bounds.rmax.y = max(bounds.rmax.y, v.y)
            bounds.rmax.z = max(bounds.rmax.z, v.z)
            bounds.rmin.x = min(bounds.rmin.x, v.x)
            bounds.rmin.y = min(bounds.rmin.y, v.y)
            bounds.rmin.z = min(bounds.rmin.z, v.z)


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
        is_road = 'road' in n.name.lower()
        for geom in geom_gen(n):
            _process_geom(geom, bounds, is_road)
    bounds.finalize()
    return bounds
