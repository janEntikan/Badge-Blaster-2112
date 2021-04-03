from random import choice, randint, uniform
from panda3d.core import Vec3, Shader
from .hell import BulletType, ExplosionType, SpecialType
from .common import SH_Z_SHADE_COLOR, SH_Z_SHADE_EXP
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import OnscreenText
from random import choice, random, uniform
import math

LIGHT_SHADER = Shader.load(Shader.SL_GLSL, 'assets/shaders/light.vert', 'assets/shaders/light.frag')

SLIP_STRENGTH = 45 # In degrees.
SLIP_TURN_SPEED = 120
SLIP_BUMP = 10


def clamp(n, mini, maxi):
    return max(min(n, maxi), mini)


def set_light_shader(n):
    nodes = []
    for np in n.find_all_matches('**/*light*'):
        bmin, bmax = np.get_tight_bounds()
        origin = Vec3(
            (bmax.x - bmin.x) / 2 + bmin.x,
            bmin.y,
            (bmax.z - bmin.z) / 2 + bmin.z
        )
        end = Vec3(
            (bmax.x - bmin.x) / 2 + bmin.x,
            bmax.y,
            (bmax.z - bmin.z) / 2 + bmin.z
        )
        np.set_shader(LIGHT_SHADER)
        np.set_shader_input('i_hue', base.trackgen._current_hue)
        np.set_shader_input('i_end', end)
        np.set_shader_input('i_origin', origin)
        np.set_shader_input('i_shade', SH_Z_SHADE_COLOR)
        np.set_shader_input('i_shade_exp', SH_Z_SHADE_EXP)
        np.set_shader_input('i_alpha_f', 0.1)
        nodes.append(np)
    return nodes


# Veers a number to a center within a threshold
def veer(n, amount, threshold, center=0):
    if n > center+threshold:
        n -= amount
    elif n < center-threshold:
        n += amount
    else:
        n = center
    return n


def distance(car1, car2):
    return (car1.root.get_pos().xy - car2.root.get_pos().xy).length()


class CooldownTimer():
    def __init__(self,a, b=0, repeat=0):
        self.a, self.b = a, b
        self.time = 0
        self.repeats = repeat
        self.repeat = repeat
        self.rate_multiplier = 1.0
        self.boosting = 0.0

    def ready(self):
        self.time -= base.dt
        if self.boosting:
            self.boosting -= base.dt
            if self.boosting <= 0:
                self.boosting = 0.0
                self.rate_multiplier = 1.0
                print("Fire rate boost expired")
        if self.time < 0:
            self.time = self.a * self.rate_multiplier
            return True

    def boost_rate(self, mult, howlong):
        self.rate_multiplier = 1.0 / mult
        if howlong > self.boosting:
            self.boosting = howlong


class Gun():
    def __init__(self, node):
        self.root = node
        if 'single' in node.name:
            self.timer = CooldownTimer(1,0,0)
            self.fire = self.single
        if 'rapid' in node.name:
            self.timer = CooldownTimer(0.2,0,0)
            self.fire = self.single
        elif 'full_spread'in node.name:
            self.timer = CooldownTimer(2,0,0)
            self.fire = self.full
        elif 'spread' in node.name:
            self.timer = CooldownTimer(1.5,0,0)
            self.fire = self.spread
        elif 'rocket' in node.name:
            self.timer = CooldownTimer(2,0,0)
            self.fire = self.rocket
        elif 'player' in node.name:
            self.timer = CooldownTimer(0.15,0,0)
            self.fire = self.player

    def player(self, car):
        if self.timer.ready():
            base.sfx['shoot_1'].set_play_rate(uniform(0.4,0.6))
            base.sfx['shoot_1'].play()
            y = car.speed.y + 100
            x = car.speed.x
            car.hell.spawn_single(BulletType.BULLET, self.root.get_pos(render),Vec3(0,y,0))

    def single(self, car):
        if self.timer.ready():
            base.sfx['shoot_2'].set_play_rate(uniform(0.4,0.6))
            base.sfx['shoot_2'].play()
            if 'rapid' in self.root.name:
                x = math.sin(car.root.get_y() * 0.05) * 15
            else:
                if not randint(0,2):
                    return
                elif self.root.get_x(render) > car.root.get_x():
                    x = 10
                else:
                    x = -10
            if self.root.get_y(render) > base.player.root.get_y():
                y = -10
            else:
                return
            car.hell.spawn_single(BulletType.GREEN, self.root.get_pos(render),Vec3(x,y,0))

    def full(self, car):
        if self.timer.ready():
            base.sfx['shoot_3'].set_play_rate(uniform(0.4,0.6))
            base.sfx['shoot_3'].play()
            type = BulletType.PURPLE
            pos = self.root.get_pos(render)
            velocity = car.speed
            velocity.x = 0
            velocity.y -= 5
            expand_speed = 20
            car.hell.spawn_ring(type, randint(5,10), pos, velocity, expand_speed, min_angle=-180, max_angle=0)

    def spread(self, car):
        if self.timer.ready():
            base.sfx['shoot_3'].set_play_rate(uniform(0.4,0.6))
            base.sfx['shoot_3'].play()
            type = BulletType.FIREBALL
            pos = self.root.get_pos(render)
            velocity = car.speed
            velocity.x = 0
            velocity.y -= randint(10,20)
            expand_speed = 10
            rotation = randint(-20, 20)
            car.hell.spawn_ring(type, 6, pos, velocity, expand_speed, 160 + rotation, 240 + rotation)

    def rocket(self, car):
        if self.timer.ready():
            base.sfx['impact'].play()
            car.hell.spawn_single(BulletType.PURPLE, self.root.get_pos(render),Vec3(0,-2,0))


class Car():
    def __init__(self, model):
        self.root = render.attach_new_node(model.name+'_root')
        self.model = model.copy_to(self.root)
        self.alive = True
        self.speed = Vec3()
        self.max_speed = 50
        self.min_speed = 20
        self.max_speed_normal = self.max_speed
        self.acceleration = 40
        self.steering = 200
        self.max_steering = 40
        self.track_left, self.track_right = -100, 100
        self.bump_time = 0.2
        self.light_nodes = set_light_shader(self.root)

        self.slipping = 0 #-1 is slip left, 1 is slip right
        self.guns = []
        for gun_empty in self.model.find_all_matches("**/*gun*"):
            self.guns.append(Gun(gun_empty))

    def remove(self):
        if self.root:
            base.player_hell.remove_collider(self.root)
            base.enemy_hell.remove_collider(self.root)
        self.root.remove_node()
        self.model.remove_node()

    def die(self):
        if not self.alive:
            return
        splode_type = choice((ExplosionType.SMALL, ExplosionType.MEDIUM, ExplosionType.LARGE))
        base.explosions.spawn_single(splode_type, self.root.get_pos())
        sound = 'explosion_'+str(randint(1,3))
        base.sfx[sound].play()
        base.sfx[sound].set_play_rate(uniform(0.3,0.9))
        self.remove()
        self.speed.normalize()
        self.speed *= 15
        self.alive = False

    def maybe_die(self):
        self.die()

    def fire_weapons(self):
        for gun in self.guns:
            gun.fire(self)

    def bump(self):
        x, y, z = self.root.get_pos()
        for enemy in base.enemy_fleet.cars:
            if not enemy == self:
                distance = (enemy.root.get_pos()-self.root.get_pos()).length_squared()
                if distance <= 1.5 ** 2 and not self.slipping:
                    base.specialfx.spawn_single(SpecialType.SPARKS, self.root.get_pos() + Vec3(random() - 0.5, random() - 0.5, random() - 0.5))
                    if self == base.player:
                        self.trigger_slip(enemy.root.get_x() > x)
                        enemy.trigger_slip(not enemy.root.get_x() > x)
        if x < self.track_left or x > self.track_right:
            base.specialfx.spawn_single(SpecialType.SPARKS, self.root.get_pos() + Vec3(random() - 0.5, random() - 0.5, random() - 0.5))
            if self.bump_time <= 0:
                self.maybe_die()
            else:
                if self.bump_time > 0.15:
                    self.trigger_slip(x < self.track_left)
                self.bump_time -= base.dt
        else:
            self.bump_time = 0.2

    def trigger_slip(self, left=True):
        if left:
            self.slipping = SLIP_STRENGTH
            self.speed.x = SLIP_BUMP
        else:
            self.slipping = -SLIP_STRENGTH
            self.speed.x = -SLIP_BUMP
        base.sfx['bounce'].play()
        self.speed.y -= 10
        if self.speed.y < 0:
            # Never slide backwards.
            self.speed.y = 0

    def slip(self, x):
        self.slipping -= (x*SLIP_TURN_SPEED) * base.dt
        if (self.slipping < 2 and self.slipping > -2) or self.slipping < -360 or self.slipping > 360:
            self.slipping = 0
        self.model.set_h(self.slipping)

    def steer(self, x):
        if self.speed.y > 0:
            self.speed.x += (x * self.steering) * base.dt
            # if self.speed.y < self.max_speed_normal:
            #     self.speed.x *= max((self.speed.y / self.max_speed_normal) ** 0.25, 0.1)
            if hasattr(self, 'max_speed_turbo') and self.speed.y > self.max_speed_normal:
                self.speed.x *= 1.0 - (self.speed.y / self.max_speed_turbo * 0.5) ** 5
            self.speed.x = clamp(self.speed.x, -self.max_steering, self.max_steering)
        else:
            self.speed.x = 0

    def accelerate(self):
        if self.speed.y < self.max_speed:
            accel = self.acceleration / (max(self.speed.y / self.max_speed_normal ** 0.75, 0.1))
            self.speed.y += accel * base.dt
        else:
            self.speed.y -= self.acceleration * base.dt
            if self.speed.y < self.max_speed:
                self.speed.y = self.max_speed

    def decelerate(self, multiplier=1):
        amount = self.acceleration * base.dt * multiplier
        self.speed.y = veer(self.speed.y, amount, threshold=0.2, center=self.min_speed)

    def update(self):
        for n in self.light_nodes:
            n.set_shader_input('i_hue', base.trackgen._current_hue)
        self.root.set_y(self.root, self.speed.y * base.dt)
        self.root.set_x(self.root, self.speed.x * base.dt)
        self.track_left, self.track_right = base.trackgen.query(self.root.get_y())
        if not self.slipping:
            self.model.set_h(-self.speed.x/2)
        if base.game_over:
            self.speed *= 0.995
        self.bump()



class EnemyCar(Car):
    def __init__(self, model, position):
        Car.__init__(self, model)
        self.look_ahead = 10
        self.steering = 100
        self.max_speed = 200
        self.max_speed_normal = 200
        self.min_speed = 35
        self.acceleration = 80
        self.root.set_pos(position)
        self.score_gain = 500
        self.speed.y = 10
        self.speed.x = 0
        self.aim = uniform(60, 70) # target distance they try to stay ahead of player
        self.aim_hysteresis = uniform(5, 25) # how far they are allowed to stray from aim distance
        self.last_fire = 10.0
        self.hell = base.enemy_hell
        base.player_hell.add_collider(self.root, radius=2, callback=self.get_hit)
        self.task = base.task_mgr.add(self.act)

    def remove(self):
        base.enemy_fleet.car_removed(self)
        self.task.remove()
        base.player_hell.remove_collider(self.root)
        Car.remove(self)

    async def get_hit(self, bullet_type=None):
        if not self.root:
            return

        self.hp -= 1
        if self.hp < 0:
            # Score gain flies off.
            scale = math.sqrt(self.score_gain) / 25.0
            base.add_score(self.score_gain)
            text = OnscreenText(str(self.score_gain), font=base.gui.font, parent=base.render, scale=scale, fg=(1, 1, 1, 1))
            text.set_light_off(True)
            text.set_z(10)
            text.set_pos(self.root.get_pos())
            text.set_depth_test(False)
            dir = base.player.root.get_x() - self.root.get_x()
            if dir == 0:
                dir = choice((-1, 1))
            if dir < 5:
                dir *= 5 / abs(dir)
            text.posInterval(1.0, self.root.get_pos() + (-dir, base.player.speed.y * 0.6, 0)).start()
            text.scaleInterval(1.0, scale*2).start()
            text.set_transparency(1)
            Sequence(Wait(0.25), text.colorScaleInterval(0.75, (1, 0, 0, 0))).start()
            self.die()
        else:
            self.root.set_color_scale((1, 0, 0, 1))
            await WaitInterval(0.1)
            if self.root:
                self.root.clear_color_scale()

    def chase(self):
        aim_y = base.player.root.get_y() + self.aim
        if aim_y > self.root.get_y() + self.aim_hysteresis:
            self.accelerate()
        elif aim_y < self.root.get_y() - self.aim_hysteresis:
            self.decelerate()

        nearby_cars = base.enemy_fleet.get_nearby_cars(self, 10, foresight=0.25)
        if nearby_cars:
            # Steer to avoid nearby cars.
            steer = 0
            for nearby_car in nearby_cars:
                diff = self.root.get_x() - nearby_car.root.get_x()
                if abs(diff) < 0.001:
                    # (Near-)zero, steer randomly
                    steer += choice((-5, 5))
                else:
                    steer += 5 / diff
            steer /= len(nearby_cars)
            self.steer(steer)
        elif base.player.root.get_x() > self.root.get_x()+5:
            self.steer(0.4)
        elif base.player.root.get_x() < self.root.get_x()-5:
            self.steer(-0.4)
        else:
            smoothing = (self.steering/2) * base.dt
            self.speed.x = veer(self.speed.x, smoothing, smoothing)

    def stay_on_the_road(self):
        ahead = self.root.get_pos()
        ahead += self.speed * 0.25
        left, right = base.trackgen.query(ahead.y)
        if ahead.x-5 < left:
            self.steer(1)
            self.decelerate(multiplier=0.5)
        elif ahead.x+5 > right:
            self.steer(-1)
            self.decelerate(multiplier=0.5)
        else:
            return True

    def act(self, task):
        if not base.player.alive or not self.alive:
            return task.done

        self.distance = (base.player.root.get_pos()-self.root.get_pos()).length()
        if self.distance < 150:
            self.fire_weapons()

        if not self.slipping:
            if self.stay_on_the_road():
                #if self.distance < 100:
                self.chase()
            else:
                self.decelerate()
        else:
            # Eventually reach out of slip
            self.slipping *= 0.05 ** base.dt
            self.speed.x *= 0.05 ** base.dt
            if abs(self.slipping) < 0.1:
                self.speed.x = 0
                self.slipping = 0

        self.update()
        if self.alive:
            return task.cont
        else:
            return task.done


class PlayerCar(Car):
    def __init__(self, model):
        Car.__init__(self, model)
        self.max_speed = 75
        self.turbo_threshold  = 50
        self.max_speed_error  = 40
        self.max_speed_normal = self.max_speed
        self.max_speed_turbo  = 100
        base.sfx['engine'].set_play_rate(0.1)
        base.sfx['engine'].set_loop(True)
        base.sfx['engine'].play()
        self.cam_height = 60
        base.cam.set_pos(0, -self.cam_height, self.cam_height)
        base.cam.look_at(render, (0, self.cam_height/3, 0))
        self.score = 0
        self.invincible = False

        self.hell = base.player_hell
        base.enemy_hell.add_collider(self.root, radius=0.8, callback=self.get_hit)

    async def get_hit(self, bullet_type=None):
        if self.invincible:
            return

        if base.game_over:
            return

        self.speed.y = max(self.min_speed, self.speed.y - 30)

        if not base.lose_life():
            base.enemy_hell.remove_collider(self.root)
            self.trigger_slip()
            while self.root and base.bgm.status() != 1:
                splode_type = choice((ExplosionType.SMALL, ExplosionType.MEDIUM, ExplosionType.LARGE))
                base.explosions.spawn_single(splode_type, self.root.get_pos() + Vec3(random() - 0.5, random() - 0.5, 0), self.speed)
                await Wait(0.3 * random())
            base.reset_game()
            return
        base.sfx['explosion_1'].play()
        base.explosions.spawn_single(ExplosionType.SMALL, self.root.get_pos(), self.speed)
        #self.trigger_slip()
        self.invincible = True

        for i in range(10):
            await Wait(0.1)
            self.root.hide()
            await Wait(0.1)
            self.root.show()
            base.sfx['pong_hi'].play()

        self.invincible = False

    def maybe_die(self):
        if self.invincible:
            return

        if not base.game_over:
            base.task_mgr.add(self.get_hit())

    def handle_turbo(self, on=False):
        if on:
            if self.speed.y > self.turbo_threshold:
                self.max_speed = self.max_speed_turbo
            else:
                self.max_speed = self.max_speed_error
        else:
            self.max_speed = self.max_speed_normal

    def input(self, dt):
        if self.alive and not base.game_over:
            context = base.device_listener.read_context('player')
            if not self.slipping:
                base.sfx['slide'].stop()
                self.handle_turbo(context['accelerate'])
                if base.game_over:
                    self.speed.y *= 0.5 ** dt
                elif not context['decelerate']:
                    self.accelerate()
                else:
                    self.decelerate()
                if context['move']:
                    self.steer(context['move'])
                else:
                    smoothing = (self.steering/2) * base.dt
                    self.speed.x = veer(self.speed.x, smoothing, smoothing)

                # Always fire while boosting fire rate so effect is more obvious
                if not base.game_over and (len(base.enemy_fleet.cars) > 0 or self.guns[0].timer.boosting):
                    self.fire_weapons()
            else:
                if not base.sfx['slide'].status() == 0:
                    base.sfx['slide'].play()
                self.slip(context['move'])

        last_y = self.root.get_y()
        self.update()
        base.add_score(self.root.get_y() - last_y)

        engine_rate = ((self.speed.y/self.max_speed_turbo)*2)
        base.sfx['engine'].set_play_rate(engine_rate)
        engine_volume = max(0,(self.speed.y/self.max_speed_turbo)/3)
        base.sfx['engine'].set_volume(engine_volume)

        # Set counters
        color = (1,1,1,0.8)
        if self.slipping or self.max_speed == self.max_speed_error:
            color = (1,0,0,0.8)
        elif self.max_speed == self.max_speed_turbo:
            color = (1,1,1,0.8)
        elif self.speed.y > self.turbo_threshold:
            color = (0,1,0,0.8)
        base.gui.set_speed_counter(int((self.speed.y*2)-0.5), color)
        base.trackgen.update(self.root.get_pos())
        base.cam.set_pos(base.camx, -self.cam_height+self.root.get_y(), self.cam_height)


class EnemyFleet:
    def __init__(self):
        self.cars = set()
        self.wave_counter = 0
        self.wave_car_count = {0: 0}

    def reset(self):
        for car in tuple(self.cars):
            car.remove()

        assert not self.cars

        self.wave_counter = 0
        self.wave_car_count = {0: 0}

    def car_removed(self, car):
        if car in self.cars:
            self.cars.remove(car)
            self.wave_car_count[car.wave] -= 1
            if self.wave_car_count[car.wave] == 0:
                self.wave_killed(car)

    def wave_killed(self, car):
        # Last car in wave killed.  Powerup?  Chance increases with low health.
        #print("Killed wave", car.wave)
        chance = 0.31 - 0.1 * base.num_lives
        if chance <= 0:
            return

        if random() < chance:
            base.powerups.spawn_single(0, car.root.get_pos(), Vec3(-0.001, 0, 0))
        elif random() < 0.25:
            # 25% chance of fire rate boost.
            base.powerups.spawn_single(1, car.root.get_pos(), Vec3(0.001, 0, 0))

    def get_closest_car(self, car, max_dist=None):
        max_dist_sq = max_dist * max_dist if max_dist is not None else math.inf

        pos = car.root.get_pos().xy
        min_dist_sq = math.inf
        min_car = None

        for other in self.cars:
            if car is other:
                continue

            dist_sq = (other.root.get_pos().xy - pos).length_squared()
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                min_car = other

        if min_dist_sq <= max_dist_sq:
            return min_car

    def get_nearby_cars(self, car, max_dist, foresight=0.0):
        max_dist_sq = max_dist * max_dist

        pos = (car.root.get_pos() + car.speed * foresight).xy
        cars = []

        for other in self.cars:
            if car is other:
                continue

            dist_sq = ((other.root.get_pos() + other.speed * foresight).xy - pos).length_squared()
            if dist_sq < max_dist_sq:
                cars.append(other)

        return cars

    def make_car(self, c, point):
        cars = [
            "cop_car_s",
            "cop_car_m",
            "cop_car_l",
            "cop_truck",
            "tank",
        ]
        if c > 4:
            c = 4
        car = EnemyCar(base.models["cars"][cars[c]], point)
        car.score_gain = int(10 * (c + 1) * (base.difficulty + 1)) * 50

        car.wave = self.wave_counter
        self.wave_car_count[car.wave] += 1

        car.hp = c+1*2 # not really random
        if c == 4:
            car.hp = 14
        self.cars.add(car)
        return car

    def spawn(self, y, left, right):
        diff = base.trackgen._difficulty

        c = 0
        for i in range(int(diff*5)):
            if randint(0,1):
                c+=1
        if random() < 0.15 and diff > 0.3:
            print("Lucky enemy promotion")
            c += randint(1, 2)

        if c == 0:
            num_cars = int(3 + diff * 6)
        elif c == 1:
            num_cars = int(1.5 + diff * 4)
        elif c == 2:
            num_cars = int(1 + diff * 2)
        else:
            num_cars = 1

        width = right - left - 20

        if num_cars == 1:
            x = uniform(left + 10, right - 10)
            self.make_car(c, Vec3(x, y, 0))
        elif num_cars > 4:
            # 2 rows
            row1_cars = num_cars // 2
            row1_mult = width / (row1_cars - 1)
            for i in range(row1_cars):
                x = left + 10 + i * row1_mult
                self.make_car(c, Vec3(x, y + random() - 0.5, 0))

            row2_cars = num_cars - row1_cars
            row2_mult = width / (row2_cars - 1)
            for i in range(row2_cars):
                x = left + 10 + i * row2_mult
                self.make_car(c, Vec3(x, y + 20 + random() - 0.5, 0))

        elif num_cars > 0:
            mult = width / (num_cars - 1)
            for i in range(num_cars):
                x = left + 10 + i * mult
                self.make_car(c, Vec3(x, y + random() - 0.5, 0))

        self.wave_counter += 1
        self.wave_car_count[self.wave_counter] = 0
