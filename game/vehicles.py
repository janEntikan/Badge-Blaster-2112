from random import choice, randint, uniform
from panda3d.core import Vec3
from .hell import BulletType, ExplosionType, SpecialType
from direct.interval.IntervalGlobal import *
from random import choice, random


SLIP_STRENGTH = 45 # In degrees.
SLIP_TURN_SPEED = 120
SLIP_BUMP = 10


def clamp(n, mini, maxi):
    return max(min(n, maxi), mini)


# Veers a number to a center within a threshold
def veer(n, amount, threshold, center=0):
    if n > center+threshold:
        n -= amount
    elif n < center-threshold:
        n += amount
    else:
        n = center
    return n


class CooldownTimer():
    def __init__(self,a, b=0, repeat=0):
        self.a, self.b = a, b
        self.time = a
        self.repeats = repeat
        self.repeat = repeat

    def ready(self):
        self.time -= base.dt
        if self.time < 0:
            self.time = self.a
            return True

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
            self.timer = CooldownTimer(1,0,0)
            self.fire = self.full
        elif 'spread' in node.name:
            self.timer = CooldownTimer(1,0,0)
            self.fire = self.spread
        elif 'rocket' in node.name:
            self.timer = CooldownTimer(2,0,0)
            self.fire = self.rocket
        elif 'player' in node.name:
            self.timer = CooldownTimer(0.2,0,0)
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
            if not randint(0,2):
                return
            if self.root.get_x(render) > car.root.get_x():
                x = 10
            else:
                x = -10
            if self.root.get_y(render) > base.player.root.get_y():
                y = -40
            else:
                y = 40
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
            car.hell.spawn_ring(type, randint(10,20), pos, velocity, expand_speed)

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
            car.hell.spawn_ring(type, 5, pos, velocity, expand_speed, 140 + rotation, 220 + rotation)

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
        self.min_speed = 0
        self.max_speed_normal = self.max_speed
        self.acceleration = 40
        self.steering = 200
        self.max_steering = 40
        self.track_left, self.track_right = -100, 100
        self.bump_time = 0.2

        self.slipping = 0 #-1 is slip left, 1 is slip right
        self.guns = []
        for gun_empty in self.model.find_all_matches("**/*gun*"):
            self.guns.append(Gun(gun_empty))

    def die(self):
        if not self.alive:
            return
        splode_type = choice((ExplosionType.SMALL, ExplosionType.MEDIUM, ExplosionType.LARGE))
        base.explosions.spawn_single(splode_type, self.root.get_pos())
        sound = 'explosion_'+str(randint(1,3))
        base.sfx[sound].play()
        base.sfx[sound].set_play_rate(uniform(0.3,0.9))
        self.root.remove_node()
        self.model.remove_node()
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
                distance = (enemy.root.get_pos()-self.root.get_pos()).length()
                if distance <= 1.5 and not self.slipping:
                    base.specialfx.spawn_single(SpecialType.SPARKS, self.root.get_pos() + Vec3(random() - 0.5, random() - 0.5, random() - 0.5))
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
        self.root.set_y(self.root, self.speed.y * base.dt)
        self.root.set_x(self.root, self.speed.x * base.dt)
        self.track_left, self.track_right = base.trackgen.query(self.root.get_y())
        if not self.slipping:
            self.model.set_h(-self.speed.x/2)
        self.bump()



class EnemyCar(Car):
    def __init__(self, model, position):
        Car.__init__(self, model)
        self.look_ahead = 10
        self.steering = 100
        self.max_speed = 100
        self.min_speed = 35
        self.acceleration = 80
        self.root.set_pos(position)
        self.speed.y = self.max_speed
        self.speed.x = 0
        self.aim = randint(30,60)
        self.last_fire = 10.0
        self.hell = base.enemy_hell
        base.player_hell.add_collider(self.root, radius=2, callback=self.get_hit)

    def die(self):
        Car.die(self)
        base.enemy_fleet.remove_car(self)
        base.player_hell.remove_collider(self.root)

    async def get_hit(self):
        self.hp -= 1
        if self.hp < 0:
            self.die()
        elif self.root:
            self.root.set_color_scale((1, 0, 0, 1))
            await WaitInterval(0.1)
            if self.root:
                self.root.clear_color_scale()


    def chase(self):
        if base.player.root.get_x() > self.root.get_x()+5:
            self.steer(1)
        elif base.player.root.get_x() < self.root.get_x()-5:
            self.steer(-1)
        else:
            smoothing = (self.steering/2) * base.dt
            self.speed.x = veer(self.speed.x, smoothing, smoothing)
        if base.player.root.get_y()+self.aim > self.root.get_y():
            self.accelerate()
        else:
            self.decelerate()

    def stay_on_the_road(self):
        ahead = self.root.get_pos()
        ahead.y += self.speed.y/4
        left, right = base.trackgen.query(ahead.y)
        if ahead.x-10 < left:
            self.steer(2)
            self.decelerate(multiplier=0.5)
        elif ahead.x+10 > right:
            self.steer(-2)
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
                if self.distance < 100:
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
        self.turbo_threshold  = self.max_speed - 10
        self.max_speed_error  = 40
        self.max_speed_normal = self.max_speed
        self.max_speed_turbo  = 150
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

    async def get_hit(self):
        if self.invincible:
            return

        if base.game_over:
            return

        if not base.lose_life():
            self.trigger_slip()
            base.explosions.spawn_single(ExplosionType.LARGE, self.root.get_pos(), self.speed)
            while True:
                await Wait(0.3 * random())
                splode_type = choice((ExplosionType.SMALL, ExplosionType.MEDIUM, ExplosionType.LARGE))
                base.explosions.spawn_single(splode_type, self.root.get_pos() + Vec3(random() - 0.5, random() - 0.5, 0), self.speed)
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
                self.handle_turbo(context['turbo'])
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

                if not base.game_over:
                    self.fire_weapons()
            else:
                if not base.sfx['slide'].status() == 0:
                    base.sfx['slide'].play()
                self.slip(context['move'])

        self.update()
        engine_rate = ((self.speed.y/self.max_speed_turbo)*2)
        base.sfx['engine'].set_volume(max(0,(engine_rate/2)-1))
        base.sfx['engine'].set_play_rate(engine_rate)
        # Set counters
        color = (1,1,1,0.8)
        if self.slipping or self.max_speed == self.max_speed_error:
            color = (1,0,0,0.8)
        elif self.max_speed == self.max_speed_turbo:
            color = (1,1,1,0.8)
        elif self.speed.y > self.turbo_threshold:
            color = (0,1,0,0.8)
        base.gui.set_speed_counter(int((self.speed.y*2)-0.5), color)
        base.gui.set_score_counter(int(self.root.get_y()+self.score))
        base.trackgen.update(self.root.get_pos())
        base.cam.set_pos(base.camx, -self.cam_height+self.root.get_y(), self.cam_height)


class EnemyFleet:
    def __init__(self):
        self.cars = set()

    def remove_car(self, car):
        self.cars.discard(car)

    def make_car(self, c, point):
        cars = [
            "cop_car_s",
            "cop_car_m",
            "cop_car_l",
            "cop_truck",
        ]
        if c > 4:
            c = 4
        if c == 4:
            car = EnemyCar(base.models["cars"]['tank'], point)
            car.max_speed = (110 - (10*c))
        else:
            car = EnemyCar(base.models["cars"][cars[c]], point)
            car.max_speed = (110 - (10*c))

        car.hp = c+1*2 # not really random

        base.task_mgr.add(car.act)
        self.cars.add(car)
        return car

    def spawn(self, y, left, right):
        diff = base.trackgen._difficulty

        c = 0
        for i in range(int(diff*5)):
            if randint(0,1):
                c+=1

        x = (left + right) * 0.5

        if c == 0:
            self.make_car(c, Vec3(x - 8, y, 0))
            self.make_car(c, Vec3(x - 4, y, 0))
            self.make_car(c, Vec3(x, y, 0))
            self.make_car(c, Vec3(x + 4, y, 0))
            self.make_car(c, Vec3(x + 8, y, 0))
        else:
            self.make_car(c, Vec3(x, y, 0))
