from panda3d import core
import math


class LinearPattern:
    """Bullet that linearly moves in one direction."""

    lifetime = 4.0

    def __init__(self, velocity):
        self.velocity = core.Vec3(velocity)

    def update_transform(self, dt):
        return core.Mat4.translate_mat(self.velocity * dt)


class RadialPattern:
    """Expands from a point and rotates around it."""

    expand_speed = 0
    rotate_speed = 0
    lifetime = 10.0

    def __init__(self, pos, velocity, radius=1):
        self.pos = core.Point3(pos)
        self.velocity = core.Vec3(velocity)
        self.radius = radius

    def update_transform(self, dt):
        mat = core.Mat4.translate_mat(-self.pos)
        self.pos = self.pos + self.velocity * dt
        if self.expand_speed:
            cur_radius = self.radius
            self.radius += dt * self.expand_speed
            mat *= core.Mat4.scale_mat(self.radius / cur_radius)
        mat *= core.Mat4.translate_mat(self.pos)
        return mat


class BulletHell:
    def __init__(self, render=None, pool_size=1024):
        self.render = render or base.render

        self.geom_node = core.GeomNode('fireworks')
        path = self.render.attach_new_node(self.geom_node)
        path.set_render_mode_thickness(20)
        path.set_antialias(core.AntialiasAttrib.M_point)
        self.root = path

        self._generate_pool(pool_size)

        self.patterns = []
        self.pool_usage = core.SparseArray()
        self.clock = 0

    def _generate_pool(self, pool_size):
        vdata = core.GeomVertexData('piiiyeeew', core.GeomVertexFormat.get_v3t2(), core.GeomEnums.UH_static)
        vdata.set_num_rows(pool_size)

        prim = core.GeomPoints(core.GeomEnums.UH_static)
        prim.add_next_vertices(pool_size)
        geom = core.Geom(vdata)
        geom.add_primitive(prim)
        self.geom_node.remove_all_geoms()
        self.geom_node.add_geom(geom)

    def spawn_single(self, pos, velocity):
        write = self._write_bullets(1, LinearPattern(velocity))
        write(pos)

    def spawn_ring(self, num_bullets, pos, velocity, expand_speed=0, rotate_speed=0):
        pattern = RadialPattern(pos, velocity)
        pattern.expand_speed = expand_speed
        pattern.rotate_speed = rotate_speed
        pattern.radius = 0.5

        write = self._write_bullets(num_bullets, pattern)
        mult = math.pi * 2 / num_bullets
        for i in range(num_bullets):
            phi = i * mult
            write(pos + core.Vec3(math.cos(phi), math.sin(phi), 0) * pattern.radius)

    def _write_bullets(self, num_bullets, pattern):
        geom = self.geom_node.modify_geom(0)
        vdata = geom.modify_vertex_data()

        lowest_off = self.pool_usage.get_lowest_on_bit()
        if lowest_off >= num_bullets:
            # Write new bullets near beginning.
            offset = lowest_off - num_bullets
        else:
            # Write new bullets after the end.
            offset = self.pool_usage.get_highest_on_bit() + 1
        range = core.SparseArray.range(offset, num_bullets)
        self.pool_usage |= range
        #print("Allocating", range, "used range", self.pool_usage)

        old_size = vdata.get_num_rows()
        req_size = offset + num_bullets
        if old_size < req_size:
            print("Hell is too small, resizing to ", req_size)
            vdata.set_num_rows(req_size)
            geom.modify_primitive(0).add_next_vertices(req_size - old_size)

        pattern.life_expectancy = self.clock + pattern.lifetime
        pattern.range = range
        self.patterns.append(pattern)

        writer = core.GeomVertexWriter(vdata, 'vertex')
        writer.set_row(offset)
        return writer.set_data3

    def update(self, dt):
        if dt == 0:
            return

        geom = self.geom_node.modify_geom(0)
        vdata = geom.modify_vertex_data()

        for pattern in self.patterns[:]:
            if self.clock >= pattern.life_expectancy:
                #TODO: delete bullets
                range = pattern.range
                vdata.transform_vertices(core.Mat4.translate_mat((0, 0, -10000)), range)
                self.patterns.remove(pattern)
                self.pool_usage &= ~range
                #print("Freeing", range)
            else:
                vdata.transform_vertices(pattern.update_transform(dt), pattern.range)

        self.clock += dt

