import sys

try:
    from panda3d.core import PandaSystem
    import keybindings
except ImportError as ex:
    print("You have not installed the required dependencies!")
    print("Please run:")
    print("")
    print("  python -m pip install -r requirements.txt")
    print("")
    print("The error was:", ex)
    sys.exit(1)


pv = (PandaSystem.major_version, PandaSystem.minor_version, PandaSystem.sequence_version)
if pv < (1, 10, 9):
    print(f"Your version of Panda3D is too old!  You have {PandaSystem.version_string} but need 1.10.9.")
    print("Please run:")
    print("")
    print("  python -m pip install -r requirements.txt")
    print("")
    sys.exit(1)

import os
import random
s = random.randint(-(2**31), 2**31 - 1)
random.seed(s)
print('Using seed: ', s)

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DGG
from direct.fsm.FSM import FSM
from direct.gui.DirectLabel import DirectLabel
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

from game.nameEntry import NameEntry
from game.mainMenu import GUI as MainMenu
from game.highscore import GUI as Highscore

from game.lbclient import LeaderBoard

import asyncio
from direct.stdpy import thread
from lbserver import server

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


class Base(ShowBase, FSM):
    def __init__(self):
        ShowBase.__init__(self)

        # Scale window size based on DPI
        default_props = core.WindowProperties.default
        zoom = base.pipe.display_zoom
        x_size = int(round(default_props.get_x_size() * zoom))
        y_size = int(round(default_props.get_y_size() * zoom))
        self.win.request_properties(core.WindowProperties(size=(x_size, y_size)))

        self.disable_mouse()

        # panda3d_keybindings needs this
        os.chdir(core.Filename(self.main_dir).to_os_specific())

        self.device_listener = DeviceListener(SinglePlayerAssigner())
        FSM.__init__(self, "FSM-Game")
        self.set_background_color(0,0,0)
        #self.set_background_color(20/255, 16/255, 16/255, 1)

        self.font = loader.loadFont("assets/fonts/computerspeak.ttf")
        self.font.set_pixels_per_unit(100)
        DGG.set_default_font(self.font)

        self.leaderboard = LeaderBoard()

        if not self.leaderboard.submit("AAA", -1):
            #setup local server

            self.noConnection = DirectLabel(text="NO CONNECTION TO LEADERBOARD - USING LOCAL SERVER",
                frameColor=(0,0,0,0),
                text_fg=(50.2/100,0.4/100,29.4/100,1),
                pos=(0,0,-0.93),
                scale=0.05)

            thread.start_new_thread(asyncio.run, (server.main(),))
            self.leaderboard = LeaderBoard("")

        else:
            self.noConnection = core.NodePath("dummy")

        # Setup track generator
        self.levels = ("forest", "desert", "express", "farm", "bridge", "city", "village")
        parts = {i: loader.load_model(f"assets/models/{i}.bam") for i in self.levels}
        self.part_mgr = part.PartMgr(parts, ('parts', 'props'))
        self.trackgen = TrackGenerator()

        self.enemy_fleet = EnemyFleet()
        self.trackgen.register_spawn_callback(self.enemy_fleet.spawn)

        self.bgm = None
        self.title_music = loader.load_music("assets/music/title.ogg")

        self.request("MainMenu")

    def setLocalServer(self, task):
        self.leaderboard = LeaderBoard("")
        self.request("MainMenu")

    def enterMainMenu(self):
        print("Entering state MainMenu")
        self.accept("do_start", self.request, ["Game"])
        self.accept("do_highscore", self.request, ["Highscore"])
        self.accept("do_quit", sys.exit)
        self.mainMenu = NameEntry(["< START >", "< HIGHSCORE >", "< QUIT GAME >"], True)
        self.background = loader.load_model("assets/models/menuBack.bam")
        set_faux_lights(self.background)
        self.background.reparent_to(render)

        if self.bgm != self.title_music:
            self.bgm = self.title_music
            self.bgm.set_loop(True)
            self.bgm.play()

        cardmaker = core.CardMaker("titlecard")
        cardmaker.set_frame(-0.5,0.5,-0.5,0.5)
        title_texture = loader.load_texture("assets/gui/titlecard.png")
        titlecard = render2d.attach_new_node(cardmaker.generate())
        titlecard.set_texture(title_texture)
        titlecard.set_transparency(True)
        titlecard.set_z(0.4)
        self.titlecard = titlecard

    def exitMainMenu(self):
        print("Exiting state MainMenu")
        self.ignore("do_start")
        self.ignore("do_highscore")
        self.ignore("do_quit")
        self.mainMenu.destroy()
        self.background.detach_node()
        self.background = None
        self.titlecard.detach_node()
        self.titlecard = None

    def enterHighscore(self):
        print("Entering state Highscore")
        self.accept("do_back", self.request, ["MainMenu"])
        self.highScore = Highscore()
        ival = self.highScore.lbl1.posInterval(1, self.highScore.lbl1.getPos(), (2, self.highScore.lbl1.getY(), self.highScore.lbl1.getZ()))
        ival.start()

        ival = self.highScore.lbl2.posInterval(1, self.highScore.lbl2.getPos(), (2, self.highScore.lbl2.getY(), self.highScore.lbl2.getZ()))
        ival.start()

        ival = self.highScore.lbl3.posInterval(1, self.highScore.lbl3.getPos(), (2, self.highScore.lbl3.getY(), self.highScore.lbl3.getZ()))
        ival.start()

        ival = self.highScore.lbl4.posInterval(1, self.highScore.lbl4.getPos(), (2, self.highScore.lbl4.getY(), self.highScore.lbl4.getZ()))
        ival.start()

        ival = self.highScore.lbl5.posInterval(1, self.highScore.lbl5.getPos(), (2, self.highScore.lbl5.getY(), self.highScore.lbl5.getZ()))
        ival.start()

        ival = self.highScore.lbl6.posInterval(1, self.highScore.lbl6.getPos(), (2, self.highScore.lbl6.getY(), self.highScore.lbl6.getZ()))
        ival.start()

        ival = self.highScore.lbl7.posInterval(1, self.highScore.lbl7.getPos(), (2, self.highScore.lbl7.getY(), self.highScore.lbl7.getZ()))
        ival.start()

        ival = self.highScore.lbl8.posInterval(1, self.highScore.lbl8.getPos(), (2, self.highScore.lbl8.getY(), self.highScore.lbl8.getZ()))
        ival.start()

        ival = self.highScore.lbl9.posInterval(1, self.highScore.lbl9.getPos(), (2, self.highScore.lbl9.getY(), self.highScore.lbl9.getZ()))
        ival.start()

        ival = self.highScore.lbl10.posInterval(1, self.highScore.lbl10.getPos(), (2, self.highScore.lbl10.getY(), self.highScore.lbl10.getZ()))
        ival.start()

    def exitHighscore(self):
        print("Exiting state Highscore")
        self.ignore("do_back")
        self.highScore.destroy()

    def enterGame(self):
        print("Entering state Game")
        self.noConnection.hide()

        # self.disable_mouse()  # FIXME: Uncomment before release
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
        self.task_mgr.do_method_later(0.1, self.tick, name='tick')

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
        self.progress = 0.0
        self.gui.set_score_counter(self.score)

        self.bgm = None
        self.playlist = [self.loader.load_music(track) for track in SND_BGM]
        first = self.playlist.pop(0)
        random.shuffle(self.playlist)
        self.playlist.insert(0, first)
        self.track = 0

        if core.ConfigVariableBool('esc-to-exit', False).get_value():
            self.accept('escape', sys.exit)
        if core.ConfigVariableBool('god-mode', False).get_value():
            self.player.invincible = True
        self.musicManager.set_volume(
            core.ConfigVariableDouble('audio-music-volume', 1.0).get_value()
        )

        self.accept('f12', self.screenshot)
        self.accept('d', self.player.get_hit)

        self.trackgen.update(core.Vec3(0))

    def exitGame(self):
        print("Exiting state Game")

        self.sfx['engine'].stop()
        self.sfx['slide'].stop()

        self.noConnection.show()

        self.game_over = True
        self.player.remove()
        self.trackgen.reset()

        self.enemy_fleet.reset()
        self.player_hell.reset()
        self.enemy_hell.reset()
        self.explosions.reset()
        self.specialfx.reset()
        self.powerups.reset()

        taskMgr.remove('tick')
        self.gui.destroy()

        if self.bgm:
            self.bgm.stop()
        self.chk_bgm()

    def enterNameEntry(self):
        print("Entering state NameEntry")
        self.set_background_color(0,0,0)
        if self.bgm:
            self.bgm.stop()
        self.bgm = loader.load_music("assets/music/highscore.ogg")
        self.bgm.set_loop(True)
        self.bgm.play()
        #self.set_background_color(20/255, 16/255, 16/255, 1)
        self.accept("nameEntryDone", self.request, ["Highscore"])
        self.ne = NameEntry()

    def exitNameEntry(self):
        print("Exiting state NameEntry")
        print(self.ne.get())
        print(self.score)
        self.leaderboard.submit(self.ne.get(), int(self.score))
        self.ne.destroy()

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
        if self.player.invincible:
            return True
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
        if self.game_over:
            return

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
        self.dt = (1/60.0) if task.frame == 0 else globalClock.get_dt()
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
