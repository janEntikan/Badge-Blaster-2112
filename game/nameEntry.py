from panda3d.core import TextNode
from panda3d.core import NodePath
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.interval.LerpInterval import LerpHprInterval
import string
from math import cos, sin, pi

SIGNS = list(string.ascii_uppercase) + ["end"]

class NameEntry:
    def __init__(self):
        self.font = loader.load_font("assets/fonts/computerspeak.ttf")
        try:
            self.font.setPixelsPerUnit(100)
        except:
            #HACK: somehow this results in an exception sometimes
            pass

        base.cam.set_pos(0,0,0)
        base.cam.set_hpr(0,0,0)

        self.ival = None
        self.currentSign = 0
        self.currentFrameID = 0
        self.currentFrame = None

        self.spinnerNode = NodePath("spinner")
        self.spinnerNode.setPos(0, 3, -0.2)
        self.spinnerNode.setHpr(-90, 0, 0)
        self.spinnerNode.setShaderAuto(True)

        size=(-0.15,0.15,-0.05,0.375)
        z = 0.5

        self.help = DirectLabel(text="left/right = Choose sign | up = Select sign | down = remove/back",
            frameColor=(0,0,0,0),
            pos=(0,0,-0.8),
            scale=0.07)

        self.first = DirectFrame(text="", frameSize=size, pos=(-0.4,0,z), text_scale=0.35, text_font=self.font, text_align=TextNode.ACenter)
        self.second = DirectFrame(text="", frameSize=size, pos=(0,0,z), text_scale=0.35, text_font=self.font, text_align=TextNode.ACenter)
        self.third = DirectFrame(text="", frameSize=size, pos=(0.4,0,z), text_scale=0.35, text_font=self.font, text_align=TextNode.ACenter)

        self.currentFrame = self.first

        self.arrowA = DirectFrame(frameSize=(-0.1, 0.1, -0.1, 0.1), frameColor=(0,0,0,0), pos=(-0.4,0,z-0.15), image="assets/gui/arrow.png", image_scale=0.2, scale=0.5)
        self.arrowA.setTransparency(1)
        self.arrowB = DirectFrame(frameSize=(-0.1, 0.1, -0.1, 0.1), frameColor=(0,0,0,0), pos=(0,0,-0.5), image="assets/gui/arrow.png", image_scale=0.2, scale=0.5)
        self.arrowB.setTransparency(1)

        base.accept("arrow_left", self.rotateLeft)
        base.accept("arrow_right", self.rotateRight)
        base.accept("arrow_up", self.addSign)
        base.accept("arrow_down", self.removeSign)

        r = 1

        for i, sign in enumerate(SIGNS):
            deg = 2 * pi / len(SIGNS)
            t = deg * i
            x = r*cos(t)
            y = r*sin(t)
            s = TextNode(sign)
            s.setText(sign)
            s.setAlign(TextNode.ACenter)
            s.setFont(self.font)
            s.setTextColor(0,0,0,1)

            snp = self.spinnerNode.attachNewNode(s)
            snp.setScale(0.2)
            if sign == "end":
                snp.setScale(0.1)
            snp.setPos(x, y, 0)
            snp.setHpr(90 + i * (360/len(SIGNS)), 0, 0)

            self.spinnerNode.reparentTo(render)

    def destroy(self):


        base.ignore("arrow_left")
        base.ignore("arrow_right")
        base.ignore("arrow_up")
        base.ignore("arrow_down")

        self.spinnerNode.removeNode()
        self.first.destroy()
        self.second.destroy()
        self.third.destroy()
        self.arrowA.destroy()
        self.arrowB.destroy()
        self.help.destroy()

    def addSign(self):
        if SIGNS[self.currentSign] == "end":
            base.messenger.send("nameEntryDone")
            return

        self.currentFrame.setText(SIGNS[self.currentSign])
        if self.currentFrameID < 2:
            self.arrowA.setX(self.arrowA.getX() + 0.4)
            self.currentFrameID += 1
            if self.currentFrameID == 0:
                self.currentFrame = self.first
            elif self.currentFrameID == 1:
                self.currentFrame = self.second
            elif self.currentFrameID == 2:
                self.currentFrame = self.third

    def removeSign(self):
        if self.currentFrame["text"] != "":
            self.currentFrame.setText("")
            return

        if self.currentFrameID > 0:
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
        if self.ival is not None:
            self.ival.finish()
        self.ival = LerpHprInterval(self.spinnerNode, 0.25, (self.spinnerNode.getH() + 360/len(SIGNS), 0, 0))
        self.ival.start()
        self.currentSign -= 1
        if self.currentSign < 0:
            self.currentSign = len(SIGNS)-1

    def rotateRight(self):
        if self.ival is not None:
            self.ival.finish()
        self.ival = LerpHprInterval(self.spinnerNode, 0.25, (self.spinnerNode.getH() - 360/len(SIGNS), 0, 0))
        self.ival.start()
        self.currentSign += 1
        if self.currentSign >= len(SIGNS):
            self.currentSign = 0
