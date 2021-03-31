from random import choice, randint
from panda3d.core import Vec3
from .hell import BulletHell, BulletType


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


class Car():
    def __init__(self, model):
        self.root = render.attach_new_node(model.name+'_root')
        self.model = model.copy_to(self.root)

        self.speed = Vec3()
        self.max_speed = 60
        self.max_speed_normal = self.max_speed
        self.acceleration = 40
        self.steering = 200
        self.max_steering = 40
        self.track_left, self.track_right = -100, 100

        self.slipping = 0 #-1 is slip left, 1 is slip right

        self.hell = BulletHell()

    def bump(self):
        x, y, z = self.root.get_pos()
        for enemy in base.enemies:
            if not enemy == self:
                distance = (enemy.root.get_pos()-self.root.get_pos()).length()
                if distance <= 1.5:
                    self.trigger_slip(enemy.root.get_x() > x)
                    enemy.trigger_slip(not enemy.root.get_x() > x)
        if x < self.track_left or x > self.track_right:
            if self.slipping:
                #TODO: EXPLODE IN FIERY DEATH!
                pass
            else:
                self.trigger_slip(x < self.track_left)

    def trigger_slip(self, left=True):
        if left:
            self.slipping = SLIP_STRENGTH
            self.speed.x = SLIP_BUMP
        else:
            self.slipping = -SLIP_STRENGTH
            self.speed.x = -SLIP_BUMP

    def slip(self, x):
        self.slipping -= (x*SLIP_TURN_SPEED) * base.dt
        if (self.slipping < 2 and self.slipping > -2) or self.slipping < -360 or self.slipping > 360:
            self.slipping = 0
        self.model.set_h(self.slipping)

    def steer(self, x):
        if self.speed.y > 0:
            self.speed.x += (x * self.steering) * base.dt
            if self.speed.y < self.max_speed_normal:
                self.speed.x *= max((self.speed.y / self.max_speed_normal) ** 0.25, 0.1)
            self.speed.x = clamp(self.speed.x, -self.max_steering, self.max_steering)
        else:
            self.speed.x = 0

    def accelerate(self):
        if self.speed.y < self.max_speed:
            accel = self.acceleration / (max(self.speed.y / self.max_speed_normal ** 0.75, 0.1))
            self.speed.y += accel * base.dt
        else:
            self.speed.y -= self.acceleration * base.dt

    def decelerate(self, center=0, multiplier=1):
        amount = self.acceleration * base.dt * multiplier
        self.speed.y = veer(self.speed.y, amount, threshold=0.2, center=center)

    def update(self):
        self.root.set_y(self.root, self.speed.y * base.dt)
        self.root.set_x(self.root, self.speed.x * base.dt)
        self.track_left, self.track_right = base.trackgen.query(self.root.get_y())
        if not self.slipping:
            self.model.set_h(-self.speed.x/2)
            self.bump()

        self.hell.update(base.dt)


class TurboCar(Car):
    def __init__(self, model):
        Car.__init__(self, model)
        self.turbo_threshold  = 50
        self.max_speed_error  = 40
        self.max_speed_normal = self.max_speed
        self.max_speed_turbo  = 120

    def handle_turbo(self, on=False):
        if on:
            if self.speed.y > self.turbo_threshold:
                self.max_speed = self.max_speed_turbo
            else:
                self.max_speed = self.max_speed_error
        else:
            self.max_speed = self.max_speed_normal

class EnemyCar(Car):
    def __init__(self, model, position):
        Car.__init__(self, model)
        self.look_ahead = 10
        self.steering = 100
        self.max_speed = 110
        self.acceleration = 60
        self.root.set_pos(position)
        self.speed.y = self.max_speed
        self.speed.x = 0
        self.aim = randint(30,60)
        self.last_fire = 10.0
        self.looking_at = loader.load_model("models/smiley.egg.pz")
        self.looking_at.reparent_to(self.root)

    def chase(self):
        if base.player.root.get_x() > self.root.get_x()+1:
            self.steer(1)
        elif base.player.root.get_x() < self.root.get_x()-1:
            self.steer(-1)
        else:
            smoothing = (self.steering/2) * base.dt
            self.speed.x = veer(self.speed.x, smoothing, smoothing)
        if base.player.root.get_y()+self.aim > self.root.get_y():
            self.accelerate()
        else:
            self.decelerate(center=35)

    def stay_on_the_road(self):
        ahead = self.root.get_pos()
        ahead.y += self.speed.y/4
        self.looking_at.set_pos(render, ahead)
        left, right = base.trackgen.query(ahead.y)
        if ahead.x-10 < left:
            self.steer(3)
            self.decelerate(multiplier=0.5, center=35)
        elif ahead.x+10 > right:
            self.steer(-3)
            self.decelerate(multiplier=0.5, center=35)
        else:
            return True

    def act(self, task):
        if not self.slipping:
            if self.stay_on_the_road():
                self.chase()
            else:
                self.decelerate(center=35)
        self.update()
        if task.time - self.last_fire > 1:
            self.fire()
            self.last_fire = task.time
        return task.cont

    def fire(self):
        self.hell.spawn_ring(BulletType.PURPLE, 30, self.root.get_pos(), self.speed, 10)


class PlayerCar(TurboCar):
    def __init__(self, model):
        TurboCar.__init__(self, model)
        self.cam_height = 60
        base.cam.set_pos(0, -self.cam_height, self.cam_height)
        base.cam.look_at(render, (0, self.cam_height/3, 0))
        self.score = 0
        base.accept('space', self.fire)

    def input(self, task):
        context = base.device_listener.read_context('player')
        if context["slip_debug"]:
            self.slipping = choice((-1, 1))

        if self.slipping:
            self.slip(context['move'])
        elif context['move']:
            self.steer(context['move'])
        else:
            smoothing = (self.steering/2) * base.dt
            self.speed.x = veer(self.speed.x, smoothing, smoothing)

        if not self.slipping:
            if context['accelerate']:
                self.handle_turbo(context['turbo'])
                self.accelerate()
            else:
                self.decelerate()
        self.update()

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

        base.cam.set_pos(0, -self.cam_height+self.root.get_y(), self.cam_height)
        return task.cont

    def fire(self):
        self.hell.spawn_single(BulletType.MISSILE, self.root.get_pos(), self.speed + (0, 60, 0))


def spawn(point):
    car = EnemyCar(base.models["cars"]["cop_car_s"], point)
    base.task_mgr.add(car.act)
    base.enemies.append(car)
