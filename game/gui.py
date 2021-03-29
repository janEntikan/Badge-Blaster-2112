from panda3d.core import TextNode
from direct.interval.IntervalGlobal import Sequence
from direct.interval.IntervalGlobal import Func, Wait


class Gui():
    def __init__(self):
        self.font = loader.load_font("assets/fonts/computerspeak.ttf")
        self.font.set_pixels_per_unit(100)
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
        #self.speed_counter.hide()

    def set_speed_counter(self, speed, color=(1,1,1,0.8)):
        self.set_text(self.speed_counter, str(speed)+" kmph", color=color, align=1)

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

