from direct.showbase.DirectObject import DirectObject
from panda3d import core
import enum
import math


FPS = 24
NUM_FRAMES = 8


class BulletType(enum.IntEnum):
    # See bullets.png
    BULLET = 0
    MISSILE = 1
    FIREBALL = 2
    GREEN = 3
    PURPLE = 4
    RESERVED0 = 5
    RESERVED1 = 6
    RESERVED2 = 7


class ExplosionType(enum.IntEnum):
    MEDIUM = 0
    LARGE = 1
    SMALL = 2


class LinearPattern:
    """Bullet that linearly moves in one direction."""

    lifetime = 4.0
    scale = 0.4

    def __init__(self, velocity):
        self.velocity = core.Vec3(velocity)

    def update_transform(self, dt):
        mat = core.Mat4.translate_mat(self.velocity * dt)
        return mat


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


class BulletHell(DirectObject):
    def __init__(self, render=None, sprite_map='', sprite_layout=(8, 8), loop=True, pool_size=1024, check_bounds=False, scale=0.02):
        self.render = render or base.render
        self.check_bounds = check_bounds
        self.scale = scale

        tex = base.loader.load_texture(sprite_map)
        tex.set_minfilter(core.SamplerState.FT_nearest)
        tex.set_magfilter(core.SamplerState.FT_nearest)
        tex.set_wrap_u(core.SamplerState.WM_repeat if loop else core.SamplerState.WM_clamp)
        tex.set_wrap_v(core.SamplerState.WM_repeat)

        self.geom_node = core.GeomNode('fireworks')
        path = self.render.attach_new_node(self.geom_node)
        path.set_render_mode_thickness(32)
        path.set_texture(tex)
        path.set_tex_gen(core.TextureStage.get_default(), core.TexGenAttrib.M_point_sprite)
        path.set_antialias(core.AntialiasAttrib.M_point)
        path.set_depth_test(True)
        path.set_depth_write(True)
        path.set_z(1.0)
        path.set_transparency(core.TransparencyAttrib.M_binary)
        path.set_shader(core.Shader.load(core.Shader.SL_GLSL, 'assets/shaders/bullet.vert', 'assets/shaders/bullet.frag'))
        path.set_shader_input('sprite_layout', sprite_layout)
        self.root = path

        self._generate_pool(pool_size)

        self.patterns = []
        self.pool_usage = core.SparseArray()
        self.clock = 0
        self.colliders = []

        self.accept('window-event', self._update_size)
        self._update_size(base.win)

    def _update_size(self, win):
        if win == base.win:
            size = min(win.size.x, win.size.y)
            self.root.set_render_mode_thickness(size * self.scale)

    def _generate_pool(self, pool_size):
        format = core.GeomVertexFormat()
        format.add_array(core.GeomVertexFormat.get_v3().get_array(0))
        format.add_array(core.GeomVertexArrayFormat('offset', 2, core.GeomEnums.NT_float32, core.GeomEnums.C_other,
                                                    'rotation', 2, core.GeomEnums.NT_float32, core.GeomEnums.C_other))

        vdata = core.GeomVertexData('piiiyeeew', core.GeomVertexFormat.register_format(format), core.GeomEnums.UH_static)
        vdata.set_num_rows(pool_size)

        writer = core.GeomVertexWriter(vdata, 'vertex')
        for i in range(pool_size):
            writer.set_data3(0, 0, -10000)

        prim = core.GeomPoints(core.GeomEnums.UH_static)
        prim.add_next_vertices(pool_size)
        geom = core.Geom(vdata)
        geom.add_primitive(prim)
        self.geom_node.remove_all_geoms()
        self.geom_node.add_geom(geom)

    def spawn_single(self, type, pos, velocity=core.Vec3.zero()):
        write = self._write_bullets(type, 1, LinearPattern(velocity))
        dir = core.Vec2(velocity[0], velocity[1])
        if not dir.normalize():
            dir.set(1, 0)
        write(pos, dir)

    def spawn_ring(self, type, num_bullets, pos, velocity, expand_speed=0, rotate_speed=0, min_angle=0, max_angle=360):
        pattern = RadialPattern(pos, velocity)
        pattern.expand_speed = expand_speed
        pattern.rotate_speed = rotate_speed
        pattern.radius = 0.5

        min_angle = math.radians(min_angle)
        max_angle = math.radians(max_angle)

        frame_offset = int(FPS * globalClock.frame_time)

        write = self._write_bullets(type, num_bullets, pattern)
        for i in range(num_bullets):
            phi = min_angle + i * (max_angle - min_angle) / num_bullets
            dir = math.cos(phi), math.sin(phi)
            write(pos + core.Vec3(*dir, 0) * pattern.radius, dir)

    def _write_bullets(self, type, num_bullets, pattern):
        geom = self.geom_node.modify_geom(0)
        vdata = geom.modify_vertex_data()

        lowest_off = self.pool_usage.get_lowest_on_bit()
        if lowest_off >= num_bullets:
            # Write new bullets near beginning.
            offset = lowest_off - num_bullets
        else:
            # Write new bullets after the end.
            offset = self.pool_usage.get_highest_on_bit() + 1
        point_range = core.SparseArray.range(offset, num_bullets)
        self.pool_usage |= point_range
        #print("Allocating", point_range, "used point_range", self.pool_usage)

        old_size = vdata.get_num_rows()
        req_size = offset + num_bullets
        if old_size < req_size:
            print("Hell is too small, resizing to ", req_size)
            vdata.set_num_rows(req_size)
            geom.modify_primitive(0).add_next_vertices(req_size - old_size)

        pattern.life_expectancy = self.clock + pattern.lifetime
        pattern.range = point_range
        self.patterns.append(pattern)

        # Offset into the texture coordinates
        offset_writer = core.GeomVertexWriter(vdata, 'offset')
        offset_writer.set_row(offset)
        frame_offset = FPS * globalClock.frame_time
        for i in range(num_bullets):
            offset_writer.add_data2(frame_offset, type)

        vertex_writer = core.GeomVertexWriter(vdata, 'vertex')
        vertex_writer.set_row(offset)
        rotate_writer = core.GeomVertexWriter(vdata, 'rotation')
        rotate_writer.set_row(offset)
        return lambda vtx, rot: vertex_writer.set_data3(*vtx) or rotate_writer.set_data2(*rot)

    def update(self, dt):
        if dt == 0:
            return

        geom = self.geom_node.modify_geom(0)
        vdata = geom.modify_vertex_data()
        rewriter = core.GeomVertexRewriter(vdata, 'vertex')

        for pattern in self.patterns[:]:
            point_range = pattern.range
            if self.clock >= pattern.life_expectancy:
                #TODO: delete bullets
                vdata.transform_vertices(core.Mat4.translate_mat((0, 0, -10000)), point_range)
                self.patterns.remove(pattern)
                self.pool_usage &= ~point_range
                #print("Freeing", point_range)
                continue

            vdata.transform_vertices(pattern.update_transform(dt), point_range)

            # Delete vertices out of bounds.
            delete_points = core.SparseArray()
            if self.colliders or self.check_bounds:
                for sri in range(point_range.get_num_subranges()):
                    begin = point_range.get_subrange_begin(sri)
                    end = point_range.get_subrange_end(sri)
                    for i in range(begin, end):
                        rewriter.set_row(i)
                        pos = rewriter.get_data2()
                        if pos.y > base.cam.get_y() + 150:
                            delete_points.set_bit(i)
                            continue
                        left, right = base.trackgen.query(pos.y)
                        if pos.x < left or pos.x > right:
                            delete_points.set_bit(i)
                        else:
                            for node, radius_sq, callback in self.colliders:
                                collider_pos = node.get_pos()
                                if (collider_pos.xy - pos).length_squared() < radius_sq:
                                    taskMgr.add(callback())
                                    delete_points.set_bit(i)

            if not delete_points.is_zero():
                vdata.transform_vertices(core.Mat4.translate_mat((0, 0, -10000)), delete_points)
                inv_delete_points = ~delete_points
                point_range &= inv_delete_points
                self.pool_usage &= inv_delete_points
                #print("Freeing", delete_points)

                if point_range.is_zero():
                    self.patterns.remove(pattern)

        self.clock += dt

    def add_collider(self, node, radius, callback):
        """Registers a collision callback.  If it returns True, the point is removed."""
        self.colliders.append((node, radius * radius, callback))

    def remove_collider(self, node):
        self.colliders = [collider for collider in self.colliders if collider[0] != node]
