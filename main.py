from random import random
from jnius import autoclass
from copy import copy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line 
from kivy.clock import Clock
from kivy.vector import Vector

Hardware = autoclass('org.renpy.android.Hardware')
w = 50.0
color = random()

def rnd():
    return random()


class MyBorderWidget(Widget):     
    def draw_border(self):
        self.canvas.clear()
        
        height = self.get_root_window().height
        width = self.get_root_window().width
        
        with self.canvas:
            Color(color, 1, 1, mode='hsv')
            l = Line(points=(width, 0.0),
            	     width=w / 4)
            l.points += [0.0, 0.0]
            l.points += [0.0, height]
            l.points += [width, height]
            l.points += [width, 0.0]

class MyPaintWidget(Widget):
    prev_angle = 0
    prev_grav = 10
    color_direction = 1

    def __init__(self, border):
        Widget.__init__(self)
        self.border = border
        border.mainw = self
        Clock.schedule_interval(self.update_color, 1 / 20.0)

    def update_color(self, *stuff):
        global color, w
        
        (_, g, __) = Hardware.accelerometerReading()
        g += 10
        diff = g - self.prev_grav
        _w = w + diff * 20
        
        if 100 > _w > 2:
            w = _w
        self.prev_grav = g
        
        (x, y, z) = Hardware.magneticFieldSensorReading()
        angle = Vector(x , y).angle((0, 1))
        angle = (angle + 180) / 360
        # angle *= 2  # Make the colors change more
        diff = (angle - self.prev_angle) * self.color_direction
        
        if 0 < (diff + color) < 1:
            diff = -diff
            self.color_direction = -self.color_direction
            
            
        self.set_color(diff + color)
        self.prev_angle = angle
        

    def set_color(self, c):
        global color
        color = c
        self.border.draw_border()
            
    def on_touch_down(self, touch):
        print(touch.x, touch.y)
        with self.canvas:
            Color(copy(color), 1, 1, mode='hsv')
            Ellipse(pos=(touch.x - (w / 2),
                                   touch.y - (w / 2)),
            	            size=(w, w))
            touch.ud['line'] = Line(points=(touch.x, touch.y),
                                                   width=w / 2)

    def on_touch_move(self, touch):
        global w
        touch.ud['line'].points += [touch.x, touch.y]


class MyPaintApp(App):
    def build(self):
       parent = Widget()
       border = MyBorderWidget()
       mainw = MyPaintWidget(border)
       
       parent.add_widget(mainw)
       parent.add_widget(border)
       
       Hardware.accelerometerEnable(True)
       Hardware.magneticFieldSensorEnable(True)
       return parent
       
if __name__ == '__main__':
    a = MyPaintApp()
    a.run()
    Hardware.magneticFieldSensorEnable(False)
    Hardware.accelerometerEnable(False)