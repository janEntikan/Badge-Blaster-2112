from panda3d.core import Vec3


class Car():
    def __init__(self, model):
        self.root = model
        self.root.reparent_to(render)

        self.current_speed = Vec3()
        self.acceleration = 0.05
        self.steering = 1.0
        self.max_speed = 1.0
             
    def steer(self, x):
        self.current_speed.x += (x * self.steering)       

    def accelerate(self):
        # TODO: increment exponentially so it takes longer and longer
        self.current_speed.y += self.acceleration

    def update(self):
        self.root.set_y(self.root, -self.current_speed.y)


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
            if self.current_speed > self.turbo_threshold:
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
        if context['accelerate']:
            self.handle_turbo(context['turbo'])
            self.accelerate()                    
        self.update()

        return task.cont
