#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file was created using the DirectGUI Designer

from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import (
    LPoint3f,
    LVecBase3f,
    LVecBase4f,
    TextNode
)

class GUI:
    def __init__(self, rootParent=None):

        x = -0.8
        y = 0.8

        xShift = 0.15
        yShift = -0.15

        self.pg7646 = DirectButton(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(-1.093750035762787, 1.268750047683716, -0.225, 0.8250000238418579),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(-0.875, 0, -0.65),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='Back',
            text_align=TextNode.A_center,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
            command=base.messenger.send,
            extraArgs=["do_back"],
            pressEffect=1,
        )
        self.pg7646.setTransparency(0)

        self.lbl1 = DirectLabel(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(0.03750000149011612, 3.3125, -0.11250001192092896, 0.699999988079071),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(x, 0, y),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='1 - AAA',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
        )
        self.lbl1.setTransparency(0)

        x += xShift
        y += yShift

        self.lbl2 = DirectLabel(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(0.03750000149011612, 3.3125, -0.11250001192092896, 0.699999988079071),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(x, 0, y),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='2 - AAA',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
        )
        self.lbl2.setTransparency(0)

        x += xShift
        y += yShift

        self.lbl3 = DirectLabel(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(0.03750000149011612, 3.3125, -0.11250001192092896, 0.699999988079071),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(x, 0, y),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='3 - AAA',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
        )
        self.lbl3.setTransparency(0)

        x += xShift
        y += yShift

        self.lbl4 = DirectLabel(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(0.03750000149011612, 3.3125, -0.11250001192092896, 0.699999988079071),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(x, 0, y),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='4 - AAA',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
        )
        self.lbl4.setTransparency(0)

        x += xShift
        y += yShift

        self.lbl5 = DirectLabel(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(0.03750000149011612, 3.3125, -0.11250001192092896, 0.699999988079071),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(x, 0, y),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='5 - AAA',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
        )
        self.lbl5.setTransparency(0)

        x += xShift
        y += yShift

        self.lbl6 = DirectLabel(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(0.03750000149011612, 3.3125, -0.11250001192092896, 0.699999988079071),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(x, 0, y),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='6 - AAA',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
        )
        self.lbl6.setTransparency(0)

        x += xShift
        y += yShift

        self.lbl7 = DirectLabel(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(0.03750000149011612, 3.3125, -0.11250001192092896, 0.699999988079071),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(x, 0, y),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='7 - AAA',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
        )
        self.lbl7.setTransparency(0)

        x += xShift
        y += yShift

        self.lbl8 = DirectLabel(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(0.03750000149011612, 3.3125, -0.11250001192092896, 0.699999988079071),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(x, 0, y),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='8 - AAA',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
        )
        self.lbl8.setTransparency(0)

        x += xShift
        y += yShift

        self.lbl9 = DirectLabel(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(0.03750000149011612, 3.3125, -0.11250001192092896, 0.699999988079071),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(x, 0, y),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='9 - AAA',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
        )
        self.lbl9.setTransparency(0)

        x += xShift
        y += yShift

        self.lbl10 = DirectLabel(
            frameColor=(0.8, 0.8, 0.8, 0.0),
            frameSize=(0.03750000149011612, 3.3125, -0.11250001192092896, 0.699999988079071),
            hpr=LVecBase3f(0, 0, 0),
            pos=LPoint3f(x, 0, y),
            scale=LVecBase3f(0.1, 0.1, 0.1),
            text='10 - AAA',
            text_align=TextNode.A_left,
            text_scale=(1, 1),
            text_pos=(0, 0),
            text_fg=LVecBase4f(0, 0, 0, 1),
            text_bg=LVecBase4f(0, 0, 0, 0),
            text_wordwrap=None,
            parent=rootParent,
        )
        self.lbl10.setTransparency(0)


    def show(self):
        self.pg7646.show()
        self.lbl1.show()
        self.lbl2.show()
        self.lbl3.show()
        self.lbl4.show()
        self.lbl5.show()
        self.lbl6.show()
        self.lbl7.show()
        self.lbl8.show()
        self.lbl9.show()
        self.lbl10.show()

    def hide(self):
        self.pg7646.hide()
        self.lbl1.hide()
        self.lbl2.hide()
        self.lbl3.hide()
        self.lbl4.hide()
        self.lbl5.hide()
        self.lbl6.hide()
        self.lbl7.hide()
        self.lbl8.hide()
        self.lbl9.hide()
        self.lbl10.hide()

    def destroy(self):
        self.pg7646.destroy()
        self.lbl1.destroy()
        self.lbl2.destroy()
        self.lbl3.destroy()
        self.lbl4.destroy()
        self.lbl5.destroy()
        self.lbl6.destroy()
        self.lbl7.destroy()
        self.lbl8.destroy()
        self.lbl9.destroy()
        self.lbl10.destroy()