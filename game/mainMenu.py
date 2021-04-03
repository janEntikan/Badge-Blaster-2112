#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectButton import DirectButton
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f,
    TextNode
)

class GUI:
    def __init__(self, rootParent=None):

        self.btnStart = DirectButton(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(-1.63125, 1.7312501430511475, -0.21250001192092896, 0.8124999761581421),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-0.325, 0, 0.25),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='START',
            text_align=TextNode.A_center,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
            pressEffect=1,
            command=base.messenger.send,
            extraArgs=["do_start"]
        )
        self.btnStart.setTransparency(0)

        self.btnHighscore = DirectButton(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(-2.7499998569488526, 2.8874999046325684, -0.21250001192092896, 0.8124999761581421),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(0, 0, -0.025),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='HIGHSCORE',
            text_align=TextNode.A_center,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
            pressEffect=1,
            command=base.messenger.send,
            extraArgs=["do_highscore"]
        )
        self.btnHighscore.setTransparency(0)

        self.btnQuit = DirectButton(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(-0.049999999254941946, 2.487499809265137, -0.225, 0.8124999761581421),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(0.225, 0, -0.3),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='QUIT',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
            pressEffect=1,
            command=base.messenger.send,
            extraArgs=["do_quit"]
        )
        self.btnQuit.setTransparency(0)


    def show(self):
        self.btnStart.show()
        self.btnHighscore.show()
        self.btnQuit.show()

    def hide(self):
        self.btnStart.hide()
        self.btnHighscore.hide()
        self.btnQuit.hide()

    def destroy(self):
        self.btnStart.destroy()
        self.btnHighscore.destroy()
        self.btnQuit.destroy()
