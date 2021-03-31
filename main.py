from direct.showbase.ShowBase import ShowBase
from keybindings.device_listener import DeviceListener, SinglePlayerAssigner
from game.gui import Gui
from game.vehicles import PlayerCar, spawn
from game import part
from game.trackgen import TrackGenerator
from game.util import set_faux_lights


def child_dict(model):
    nodes = {}
    for node in model.get_children():
        node.detach_node()
        set_faux_lights(node)
        node.clear_transform()
        nodes[node.name] = node
    return nodes


class Base(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.device_listener = DeviceListener(SinglePlayerAssigner())
        self.gui = Gui()
        self.dt = 1
        self.enemies = []
        self.models = {}
        self.set_background_color(0, 0, 0, 0)
        # Setup track generator
        road_model = loader.load_model("assets/models/forest.bam")
        parts = {"forest": road_model}
        self.part_mgr = part.PartMgr(parts, ('parts', 'props'))
        self.trackgen = TrackGenerator()
        self.trackgen.register_spawn_callback(spawn)
        self.trackgen.set_difficulty(1)  # Adjust from 0..1
        # Load cars
        car_models = loader.load_model("assets/models/cars.bam")
        self.models["cars"] = child_dict(car_models)
        self.player = PlayerCar(self.models["cars"]["player"])
        self.task_mgr.add(self.player.input)
        self.task_mgr.add(self.tick)

    def tick(self, task=None):
        self.dt = globalClock.get_dt()
        return task.cont

if __name__ == "__main__":
    base = Base()
    base.run()
