from panda3d.core import TextNode
from panda3d.core import NodePath
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.interval.LerpInterval import LerpHprInterval
import string
from math import cos, sin, pi

SIGNS = list(string.ascii_uppercase) + ["end"]


class NameEntry:
    def __init__(self, items=SIGNS, menu=False):
        self.items = items
        self.menu = menu
        base.cam.set_pos(0,0,0)
        base.cam.set_hpr(0,0,0)

        self.currentSign = 0
        self.currentFrameID = 0
        self.currentFrame = None

        self.sound_lo = loader.load_sfx("assets/sfx/pong_lo.wav")
        self.sound_lo.set_volume(0.4)
        self.sound_ye = loader.load_sfx("assets/sfx/pickup.wav")
        self.sound_ye.set_volume(0.4)
        self.sound_no = loader.load_sfx("assets/sfx/bounce.wav")
        self.sound_no.set_volume(0.4)

        self.repeating = 0

        self.spinnerNode = NodePath("spinner")
        self.spinnerNode.setPos(0, 3, -0.2)
        self.spinnerNode.setHpr(-90, 0, 0)
        self.spinnerNode.setShaderAuto(True)
        size=(-0.15,0.15,-0.05,0.375)
        z = 0.5
        if menu:
            self.spinnerNode.setScale(0.6)
            self.spinnerNode.setZ(-0.4)
        else:
            self.help = DirectLabel(text="left/right = Choose sign | up = Select sign | down = remove/back",
                frameColor=(0,0,0,0),
                text_fg=(1,1,1,1),
                pos=(0,0,-0.8),
                scale=0.07)
            self.first = DirectFrame(text="", frameColor=(0,0,0,1), frameSize=size, pos=(-0.4,0,z), text_scale=0.35, text_fg=(1,1,1,1), text_font=base.font, text_align=TextNode.ACenter)
            self.second = DirectFrame(text="", frameColor=(0,0,0,1), frameSize=size, pos=(0,0,z), text_scale=0.35, text_fg=(1,1,1,1), text_font=base.font, text_align=TextNode.ACenter)
            self.third = DirectFrame(text="", frameColor=(0,0,0,1), frameSize=size, pos=(0.4,0,z), text_scale=0.35, text_fg=(1,1,1,1), text_font=base.font, text_align=TextNode.ACenter)
            self.currentFrame = self.first

            self.arrowA = DirectFrame(frameSize=(-0.1, 0.1, -0.1, 0.1), frameColor=(0,0,0,0), pos=(-0.4,0,z-0.15), image="assets/gui/arrow.png", image_scale=0.2, scale=0.5)
            self.arrowA.setTransparency(1)
            self.arrowB = DirectFrame(frameSize=(-0.1, 0.1, -0.1, 0.1), frameColor=(0,0,0,0), pos=(0,0,-0.5), image="assets/gui/arrow.png", image_scale=0.2, scale=0.5)
            self.arrowB.setTransparency(1)
        self.task = base.task_mgr.add(self.update)

        r = 1

        for i, sign in enumerate(self.items):
            deg = 2 * pi / len(self.items)
            t = deg * i
            x = r*cos(t)
            y = r*sin(t)
            s = TextNode(sign)
            s.setText(sign)
            s.setAlign(TextNode.ACenter)
            s.setFont(base.font)
            s.setTextColor(1,1,1,1)

            snp = self.spinnerNode.attachNewNode(s)
            snp.setScale(0.2)
            if sign == "end":
                snp.setScale(0.1)
            snp.setPos(x, y, 0)
            snp.setHpr(90 + i * (360/len(self.items)), 0, 0)

            self.spinnerNode.reparentTo(render)
        self.delay = 0.2

    def activate(self):
        self.sound_ye.play()
        if self.currentSign == 0:
            base.messenger.send("do_start")
        elif self.currentSign == 1:
            base.messenger.send("do_highscore")
        else:
            base.messenger.send("do_quit")

    def tick(self):
        self.delay -= globalClock.get_dt()
        if self.delay < 0:
            return True

    def update(self, task):
        if self.tick():
            context = base.device_listener.read_context('player')
            if context["move"]>0.2:
                self.rotateRight()
                if self.repeating:
                    self.delay = 0.2 * (0.9 ** self.repeating)
                    self.repeating += 1
                else:
                    self.delay = 0.2
                    self.repeating = 1
            elif context['move']<-0.2:
                self.rotateLeft()
                if self.repeating:
                    self.delay = 0.2 * (0.9 ** self.repeating)
                    self.repeating += 1
                else:
                    self.delay = 0.2
                    self.repeating = 1
            elif context["accelerate"] or context["select"]:
                self.addSign()
                self.delay = 0.2
                self.repeating = False
            elif context["decelerate"] or context["backspace"]:
                self.removeSign()
                self.delay = 0.2
                self.repeating = False
            else:
                self.delay = 0
                self.repeating = False

        if self.spinnerNode:
            desired_h = -self.currentSign * 360/len(self.items) - 90
            current_h = self.spinnerNode.get_h()
            diff = (((desired_h - current_h) + 180) % 360) - 180
            delta = diff * globalClock.dt * 10
            if abs(delta) > abs(diff):
                delta = diff
            self.spinnerNode.set_h(current_h + delta)
        return task.cont

    def destroy(self):
        self.task.remove()
        self.spinnerNode.removeNode()
        if not self.menu:
            self.first.destroy()
            self.second.destroy()
            self.third.destroy()
            self.arrowA.destroy()
            self.arrowB.destroy()
            self.help.destroy()

    def addSign(self):
        if self.menu:
            self.activate()
            return
        else:
            self.sound_ye.play()
            if self.items[self.currentSign] == "end":
                base.messenger.send("nameEntryDone")
                return
            self.currentFrame.setText(self.items[self.currentSign])
            if self.currentFrameID < 2:
                self.arrowA.setX(self.arrowA.getX() + 0.4)
                self.currentFrameID += 1
                if self.currentFrameID == 0:
                    self.currentFrame = self.first
                elif self.currentFrameID == 1:
                    self.currentFrame = self.second
                elif self.currentFrameID == 2:
                    self.currentFrame = self.third
            else:
                self.currentSign = SIGNS.index("end")

    def removeSign(self):
        if self.menu:
            self.activate()
            return
        if self.currentFrame["text"] != "":
            self.currentFrame.setText("")
            return

        if self.currentFrameID > 0:
            self.sound_no.play()
            self.arrowA.setX(self.arrowA.getX() - 0.4)
            self.currentFrameID -= 1
            if self.currentFrameID == 0:
                self.currentFrame = self.first
            elif self.currentFrameID == 1:
                self.currentFrame = self.second
            elif self.currentFrameID == 2:
                self.currentFrame = self.third

    def get(self):
        return "{}{}{}".format(self.first["text"], self.second["text"], self.third["text"])

    def rotateLeft(self):
        self.sound_lo.play()
        self.currentSign -= 1
        if self.currentSign < 0:
            self.currentSign = len(self.items)-1

    def rotateRight(self):
        self.sound_lo.play()
        self.currentSign += 1
        if self.currentSign >= len(self.items):
            self.currentSign = 0
