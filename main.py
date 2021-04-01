from direct.showbase.ShowBase import ShowBase
from panda3d import core
from keybindings.device_listener import DeviceListener, SinglePlayerAssigner
from game.gui import Gui
from game.vehicles import PlayerCar, spawn
from game import part
from game.trackgen import TrackGenerator
from game.util import set_faux_lights, spline_point
from game.followcam import FollowCam
from game.hell import BulletHell
from game.common import DF_INC_PER_SEC

core.load_prc_file(core.Filename.expand_from('$MAIN_DIR/settings.prc'))

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
        # self.disable_mouse()  # FIXME: Uncomment before release
        self.device_listener = DeviceListener(SinglePlayerAssigner())
        self.gui = Gui()
        self.dt = 1
        self.camx = 0
        self.enemies = []
        self.models = {}
        self.set_background_color(0, 0, 0, 0)
        # Setup track generator
        self.levels = ("forest", "desert", "express")
        parts = {i: loader.load_model(f"assets/models/{i}.bam") for i in self.levels}
        self.part_mgr = part.PartMgr(parts, ('parts', 'props'))
        self.trackgen = TrackGenerator()
        self.trackgen.register_spawn_callback(spawn)
        self.trackgen.set_difficulty(1)  # Adjust from 0..1

        # Load hells
        self.player_hell = BulletHell(self.render, 'assets/fireworks/bullets.png', (8, 8), check_bounds=True, scale=0.02)
        self.enemy_hell = BulletHell(self.render, 'assets/fireworks/bullets.png', (8, 8), check_bounds=True, scale=0.03)
        self.explosions = BulletHell(self.render, 'assets/fireworks/explosions.png', (12, 3), loop=False, check_bounds=False, scale=0.15)
        self.specialfx = BulletHell(self.render, 'assets/fireworks/smokesparks.png', (10, 3), loop=False, check_bounds=False, scale=0.05)

        # Load cars
        car_models = loader.load_model("assets/models/cars.bam")
        self.models["cars"] = child_dict(car_models)
        self.player = PlayerCar(self.models["cars"]["player"])
        self.task_mgr.do_method_later(0.01, self.tick, name='tick')

        # Setup x-follow cam
        self.followcam = FollowCam()
        self.accept("level-transition", self.level_transition_evt)

        # Setup difficulty adjust
        self.difficulty = spline_point(0)
        self.progress = 0
        self.task_mgr.do_method_later(1, self.update_difficulty, name="update_difficulty")

    def level_transition_evt(self, level):
        print(f"We're about to enter the level {level.upper()}")

    def tick(self, task=None):
        self.dt = globalClock.get_dt()
        self.player.input(self.dt)
        self.followcam.update(self.dt)
        self.player_hell.update(self.dt)
        self.enemy_hell.update(self.dt)
        self.explosions.update(self.dt)
        self.specialfx.update(self.dt)
        return task.cont

    def update_difficulty(self, task=None):
        self.progress += DF_INC_PER_SEC
        self.difficulty = spline_point(min(self.progress, 1.0))
        self.trackgen.set_difficulty(self.difficulty)
        print(self.difficulty)
        return task.again


if __name__ == "__main__":
    base = Base()
    base.run()
