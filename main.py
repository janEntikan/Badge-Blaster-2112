from direct.showbase.ShowBase import ShowBase
from keybindings.device_listener import DeviceListener, SinglePlayerAssigner
from vehicles import PlayerCar


def child_dict(model):
    nodes = {}
    for node in model.get_children():
        node.detach_node()
        node.clear_transform()
        nodes[node.name] = node
    return nodes


class Base(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.device_listener = DeviceListener(SinglePlayerAssigner())

        self.models = {}
        # Load cars
        car_models = loader.load_model("assets/models/cars.bam")
        self.models["cars"] = child_dict(car_models)
        self.player = PlayerCar(self.models["cars"]["player"])
        # Attach camera to player car
        base.cam.reparent_to(self.player.root)
        base.cam.set_pos(0, 40, 40)
        base.cam.look_at(self.player.root, (0,-20,0))        
        # Testroad
        self.models["testroad"] = loader.load_model("assets/models/testroad.bam")
        for i in range(20):
            r = self.models["testroad"].copy_to(render)
            r.set_y(i*-260)
        self.task_mgr.add(self.player.input)


if __name__ == "__main__":
    base = Base()
    base.run()
