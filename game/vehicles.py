from panda3d.core import Vec3


def clamp(n, mini, maxi):
    return max(min(n, maxi), mini)


class Car():
    def __init__(self, model):
        self.root = model
        self.root.reparent_to(render)

        self.acceleration = 0.03
        self.speed = Vec3()
        self.steering = 0.1
        self.max_steering = 0.5
        self.max_speed = 1.0
             
    def steer(self, x):
        self.speed.x -= (x * self.steering) * self.speed.y       
        self.speed.x = clamp(
            self.speed.x, -self.max_steering, self.max_steering
        )
        
    def accelerate(self):
        self.speed.y += self.acceleration
        self.speed.y = clamp(
            self.speed.y, 0, self.max_speed
        )

    def update(self):
        self.root.set_y(self.root, -self.speed.y)
        self.root.set_x(self.root, self.speed.x*self.speed.y)
        self.root.set_h(self.speed.x*25)
    

class TurboCar(Car):
    def __init__(self, model):
        Car.__init__(self, model)
        self.turbo_threshold  = 0.9
        self.max_speed_error  = 0.3
        self.max_speed_normal = 1.0
        self.max_speed_turbo  = 2.0
        self.max_speed = self.max_speed_normal

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
    
    def input(self, task):
        context = base.device_listener.read_context('player')
        if context['move']:
            self.steer(context['move'])
        else:
            self.speed.x /= 1.2
        if context['accelerate']:
            self.handle_turbo(context['turbo'])
            self.accelerate()                    
        else:
            self.speed.y /= 1+(self.acceleration*2)

        self.update()
        return task.cont
