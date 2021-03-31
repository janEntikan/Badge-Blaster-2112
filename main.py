from direct.showbase.ShowBase import ShowBase
from panda3d import core
from keybindings.device_listener import DeviceListener, SinglePlayerAssigner
from game.gui import Gui
from game.vehicles import PlayerCar, spawn
from game import part
from game.trackgen import TrackGenerator
from game.util import set_faux_lights
from game.followcam import FollowCam

USER_CONFIG_PATH = core.Filename.expand_from('$MAIN_DIR/user.prc')
if USER_CONFIG_PATH.exists():
    core.load_prc_file(USER_CONFIG_PATH)


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
        self.disable_mouse()
        self.device_listener = DeviceListener(SinglePlayerAssigner())
        self.gui = Gui()
        self.dt = 1
        self.camx = 0
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
        # Setup x-follow cam
        self.followcam = FollowCam()

    def tick(self, task=None):
        self.dt = globalClock.get_dt()
        self.followcam.update(self.dt)
        return task.cont

if __name__ == "__main__":
    base = Base()
    base.run()
