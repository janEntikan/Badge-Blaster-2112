from random import choice
from panda3d.core import Vec3


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
        self.model = model
        self.model.reparent_to(self.root)

        self.speed = Vec3()
        self.max_speed = 60
        self.max_speed_normal = self.max_speed
        self.acceleration = 40
        self.steering = 200
        self.max_steering = 40

        self.slipping = 0 #-1 is slip left, 1 is slip right

    def slip(self, x):
        self.speed.x = self.slipping*(self.max_steering)
        if x == -self.slipping:
            self.slipping = 0
            self.speed.x
        
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

    def update(self):
        self.root.set_y(self.root, self.speed.y * base.dt)
        self.root.set_x(self.root, self.speed.x * base.dt)
        if self.slipping:
            self.model.set_h(self.speed.x)    
        else:
            self.model.set_h(-self.speed.x/2)


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


class PlayerCar(TurboCar):
    def __init__(self, model):
        TurboCar.__init__(self, model)
        self.cam_height = 60
        base.cam.set_pos(0, -self.cam_height, self.cam_height)
        base.cam.look_at(render, (0, self.cam_height/3, 0))
    
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

        if context['accelerate']:
            self.handle_turbo(context['turbo'])
            self.accelerate()                    
        else:
            amount = self.acceleration * base.dt
            self.speed.y = veer(self.speed.y, amount, threshold=0.2)           

        self.update()
        base.cam.set_pos(0, -self.cam_height+self.root.get_y(), self.cam_height)
        return task.cont
