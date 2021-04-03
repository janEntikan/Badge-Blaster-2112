import sys
import random
s = random.randint(-(2**31), 2**31 - 1)
random.seed(s)
print('Using seed: ', s)

from direct.showbase.ShowBase import ShowBase
from panda3d import core
from keybindings.device_listener import DeviceListener, SinglePlayerAssigner
from game.gui import Gui
from game.vehicles import PlayerCar, EnemyFleet
from game import part
from game.trackgen import TrackGenerator
from game.util import set_faux_lights, spline_point
from game.followcam import FollowCam
from game.hell import BulletHell
from game.common import DF_INC_PER_SEC, SND_BGM

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
        self.models = {}
        self.set_background_color(0, 0, 0, 0)
        # Load sounds
        filenames = [
            'bounce', 'engine', 'explosion_1', 'explosion_2',
            'explosion_3', 'impact', 'pickup', 'pong_hi', 'pong_lo',
            'scratch', 'shoot_1', 'shoot_2', 'shoot_3', 'slide'
        ]
        self.sfx = {}
        for filename in filenames:

            sfx = self.sfx[filename] = loader.load_sfx('assets/sfx/'+filename+'.wav')
            sfx.set_play_rate(0.6)

        # Setup track generator
        self.levels = ("forest", "desert", "express", "farm", "bridge", "city", "village")
        parts = {i: loader.load_model(f"assets/models/{i}.bam") for i in self.levels}
        self.part_mgr = part.PartMgr(parts, ('parts', 'props'))
        self.trackgen = TrackGenerator()

        # Load hells
        self.player_hell = BulletHell(self.render, 'assets/fireworks/bullets.png', (8, 8), check_bounds=True, scale=0.02)
        self.enemy_hell = BulletHell(self.render, 'assets/fireworks/bullets.png', (8, 8), check_bounds=True, scale=0.03)
        self.explosions = BulletHell(self.render, 'assets/fireworks/explosions.png', (12, 3), loop=False, check_bounds=False, scale=0.15)
        self.specialfx = BulletHell(self.render, 'assets/fireworks/smokesparks.png', (10, 3), loop=False, check_bounds=False, scale=0.05)
        self.powerups = BulletHell(self.render, 'assets/fireworks/powerups.png', (8, 2), check_bounds=False, scale=0.05, pool_size=8)

        # Load cars
        car_models = loader.load_model("assets/models/cars.bam")
        self.models["cars"] = child_dict(car_models)
        self.player = PlayerCar(self.models["cars"]["player"])
        self.task_mgr.do_method_later(0.01, self.tick, name='tick')

        self.enemy_fleet = EnemyFleet()
        self.trackgen.register_spawn_callback(self.enemy_fleet.spawn)

        self.powerups.add_collider(self.player.root, radius=3, callback=self.pickup)

        # Setup x-follow cam
        self.followcam = FollowCam()
        self.accept("level-transition", self.level_transition_evt)

        # Setup difficulty adjust
        self.difficulty = spline_point(0)
        self.progress = 0
        self.task_mgr.do_method_later(1, self.update_difficulty, name="update_difficulty")

        self.score = 0.0
        self.num_lives = 3
        self.level_counter = 1
        self.gui.set_num_lives(self.num_lives)
        self.game_over = False

        self.bgm = None
        self.playlist = [self.loader.load_music(track) for track in SND_BGM]
        random.shuffle(self.playlist)
        self.track = 0

        if core.ConfigVariableBool('esc-to-exit', False).get_value():
            self.accept('escape', sys.exit)
        if core.ConfigVariableBool('god-mode', False).get_value():
            self.player.invincible = True
        self.musicManager.set_volume(
            core.ConfigVariableDouble('audio-music-volume', 1.0).get_value()
        )

        self.accept('f12', self.screenshot)
        self.accept('r', self.reset_game)

    def reset_game(self):
        self.num_lives = 3
        self.level_counter = 1
        self.gui.set_num_lives(self.num_lives)
        self.score = 0
        self.progress = 0.0
        self.gui.set_score_counter(self.score)
        self.game_over = False
        self.player.remove()
        self.trackgen.reset()

        self.enemy_fleet.reset()
        self.player_hell.reset()
        self.enemy_hell.reset()
        self.explosions.reset()
        self.specialfx.reset()
        self.powerups.reset()

        self.player = PlayerCar(self.models["cars"]["player"])
        self.powerups.add_collider(self.player.root, radius=2, callback=self.pickup)

        if self.bgm:
            self.bgm.stop()
        self.chk_bgm()

    def add_score(self, score):
        if not self.game_over:
            self.score += score
            self.gui.set_score_counter(int(self.score))

    async def pickup(self, type):
        if self.game_over:
            return
        self.sfx['pickup'].play()
        print("Picked up pickup of type", type)
        if type == 0:
            self.num_lives += 1
            self.gui.set_num_lives(self.num_lives)
        else:
            for gun in self.player.guns:
                # Multiply gun rate by 2.5 for 5 seconds
                gun.timer.boost_rate(2.5, 5.0)

    def lose_life(self):
        if self.game_over:
            return False
        if self.num_lives > 0:
            self.num_lives -= 1
            self.gui.set_num_lives(self.num_lives)
            if self.num_lives == 1:
                print(self.num_lives, "life left")
            else:
                print(self.num_lives, "lives left")
            return True
        else:
            print("GAME OVER!")
            self.gui.announce_game_over()
            self.bgm.stop()
            self.bgm = self.loader.load_music('assets/music/gameover.ogg')
            self.bgm.play()

            self.game_over = True
            return False

    def level_transition_evt(self, level):
        print(f"We're about to enter the level {level.upper()}")
        if level == 'express':
            level += 'way'
        elif level == 'farm':
            level += 's'
        self.gui.announce_level(self.level_counter, level)
        self.level_counter += 1

        # Throw the player a life if they have none
        if self.num_lives > 1:
            return

        # If you have one life, 50% that one spawns, decreasing with difficulty
        if self.num_lives == 1 and (random.randint(0, 1) or random.random() < self.difficulty):
            return

        y = self.player.root.get_y() + 100
        l, r = self.trackgen.query(y)
        x = (l + r) * 0.5
        self.powerups.spawn_single(0, core.Point3(x, y, 0), core.Vec3(-0.001, 0, 0))

    def tick(self, task=None):
        self.dt = globalClock.get_dt()
        self.player.input(self.dt)
        self.followcam.update(self.dt)
        self.player_hell.update(self.dt)
        self.enemy_hell.update(self.dt)
        self.explosions.update(self.dt)
        self.specialfx.update(self.dt)
        self.powerups.update(self.dt)
        self.chk_bgm()
        return task.cont

    def chk_bgm(self):
        if self.bgm is None:
            self.bgm = self.playlist[self.track]
            self.bgm.play()
            self.bgm.set_volume(0.6)
        if self.bgm.status() != self.bgm.PLAYING and not self.game_over:
            print('next track')
            self.track += 1
            self.track = self.track % len(self.playlist)
            self.bgm = self.playlist[self.track]
            self.bgm.set_volume(0.6)
            self.bgm.play()

    def update_difficulty(self, task=None):
        if not self.game_over:
            self.progress += DF_INC_PER_SEC
            self.difficulty = spline_point(min(self.progress, 1.0))
            self.trackgen.set_difficulty(self.difficulty)
            print("Difficulty is now %.1f %%" % (self.difficulty * 100))
        return task.again


if __name__ == "__main__":
    base = Base()
    base.run()
