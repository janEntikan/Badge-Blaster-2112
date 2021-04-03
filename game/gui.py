from panda3d import core
from panda3d.core import TextNode
from direct.interval.IntervalGlobal import Sequence
from direct.interval.IntervalGlobal import Func, Wait
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText


class Gui():
    def __init__(self):
        self.font = loader.load_font("assets/fonts/computerspeak.ttf")
        self.big_text = render2d.attach_new_node(TextNode('big text'))
        self.big_text.set_pos((0,0,0.1))
        self.big_text.set_scale(0.2)
        self.sequence = self.flashy_text(
            self.big_text, "COPKILL2121", [
                (1,0,0,0.2),(1,1,1,0.6),(0,0,1,0.2),(1,1,1,0.8)
            ], speed=0.4
        )
        self.sequence.loop()

        self.sub_text = render2d.attach_new_node(TextNode('sub text'))
        self.sub_text.set_pos((0,0,-0.4))
        self.sub_text.set_scale(0.05)
        self.set_text(self.sub_text, "PRESS Z TO START")
        self.big_text.hide()
        self.sub_text.hide()

        self.hud = render2d.attach_new_node('hud')
        self.speed_counter = self.hud.attach_new_node(TextNode('speed counter'))
        self.set_speed_counter(0)
        self.speed_counter.set_scale(0.1)
        self.speed_counter.set_pos(0.9,0,-0.9)

        self.score_counter = self.hud.attach_new_node(TextNode("score counter"))
        self.set_score_counter(0)
        self.score_counter.set_scale(0.05)
        self.score_counter.set_pos(-0.9,0,0.9)

        self.lives = []
        self.heart_tex = loader.load_texture('assets/gui/heart.png')
        self.heart_tex.set_minfilter(core.SamplerState.FT_nearest)
        self.heart_tex.set_magfilter(core.SamplerState.FT_nearest)

    def destroy(self):
        self.sequence.finish()
        self.big_text.removeNode()
        self.sub_text.removeNode()
        self.hud.removeNode()
        for live in self.lives:
            live.destroy()

    def announce_level(self, num, name):
        text = OnscreenText(text='LEVEL ' + str(num), font=self.font, parent=base.aspect2d, pos=(0, 0.3), scale=0.1, fg=(1, 1, 1, 1))
        text.set_transparency(1)
        text.set_color_scale((1, 1, 1, 0))
        Sequence(
            Wait(1.0),
            text.colorScaleInterval(1.0, (1, 1, 1, 1)),
            Wait(2.0),
            text.colorScaleInterval(1.0, (1, 1, 1, 0)),
            Func(text.destroy),
        ).start()

        subtext = OnscreenText(text=name.upper(), font=self.font, parent=base.aspect2d, pos=(0, 0.1), scale=0.08, fg=(1, 1, 1, 1))
        subtext.set_transparency(1)
        subtext.set_color_scale((1, 1, 1, 0))
        Sequence(
            Wait(2.0),
            subtext.colorScaleInterval(1.0, (1, 1, 1, 1)),
            Wait(2.0),
            subtext.colorScaleInterval(1.0, (1, 1, 1, 0)),
            Func(subtext.destroy),
        ).start()

    def announce_game_over(self):
        text = OnscreenText(text='GAME OVER', font=self.font, parent=base.aspect2d, pos=(0, 0.3), scale=0.1, fg=(1, 1, 1, 1))
        text.set_transparency(1)
        text.set_color_scale((1, 1, 1, 0))
        Sequence(
            text.colorScaleInterval(2.0, (1, 1, 1, 1)),
            Wait(4.0),
            text.colorScaleInterval(3.5, (1, 0, 0, 0)),
            Func(text.destroy),
        ).start()

    def set_num_lives(self, num_lives):
        while num_lives > len(self.lives):
            image = OnscreenImage(self.heart_tex, pos=(0.2 + len(self.lives) * 0.1, 0, -0.18), scale=0.04, parent=base.a2dTopLeft)
            image.set_transparency(core.TransparencyAttrib.M_binary)
            self.lives.append(image)

        while num_lives < len(self.lives):
            self.lives.pop().destroy()

    def set_speed_counter(self, speed, color=(1,1,1,0.8)):
        self.set_text(self.speed_counter, str(speed)+" kmph", color=color, align=1)

    def set_score_counter(self, score):
        self.set_text(self.score_counter, "score " + str(score).zfill(10), align=0)

    def flashy_text(self, node, text, colors, speed, align=2, repeat=1):
        sequence = Sequence()
        for r in range(repeat):
            for color in colors:
                sequence.append(Func(self.set_text, node, text, color, align))
                sequence.append(Wait(speed))
        return sequence

    def set_text(self, node, text, color=(1,1,1,1), align=2):
        text_node = node.node()
        text_node.font = self.font
        text_node.align = align
        text_node.text = text
        text_node.text_color = color

