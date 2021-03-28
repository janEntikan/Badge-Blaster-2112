from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3


def separate_nodes(model):
    nodes = {}
    for node in model.get_children():
        node.detach_node()
        node.clear_transform()
        nodes[node.name] = node
    return nodes


class Car():
    def __init__(self, model):
        self.root = model
        self.root.reparent_to(render)

        self.acceleration = 1
        self.steering = 1

        self.current_speed      = Vec3(0.0, 0.0, 0.0)
        self.max_speed_normal   = Vec3(1.0, 1.0, 1.0)
        self.max_speed_turbo    = Vec3(2.0, 2.0, 2.0)
        self.turbo_threshold    = Vec3(0.9, 0.9, 0.9)
        
    def steer(self, x):
        self.current_speed.x += (x * self.steering)       
        
    def accelerate(self, x):
        self.current_speed.y += (y * self.acceleration)


class Base(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.models = {}
        car_models = loader.load_model("assets/models/cars.bam")
        self.models["cars"] = separate_nodes(car_models)
        self.player = Car(self.models["cars"]["player"])

        base.cam.reparent_to(self.player.root)
        base.cam.set_pos(0, 40, 40)
        base.cam.look_at(self.player.root, (0,-20,0))        


if __name__ == "__main__":
    base = Base()
    base.run()
