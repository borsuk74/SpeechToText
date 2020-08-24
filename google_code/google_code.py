#This code could be built on Linux with buildozer and deployed on Android.
# When run from python on Linux it works too, actually without throwing
#unsupported platform exception
from kivy.app import App
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
import audiostream as sd

class Demo(App):
    def set_background_color(self):
        with self.label.canvas.before:
            Color(0.5, 0.0, 0.5)
            Rectangle(size=Window.size)
    def _resize_handler(self,obj,size):
        self.set_background_color()

    def on_start(self):
        symbols = ''
        for m in dir(sd):
            symbols += m + '\n'
            self.label.text = symbols

    def build(self):
        Window.bind(size=self._resize_)
        self.label = Label(text = 'Greetings Earthlings')
        self.set_background_color()
        return self.label

if __name__ == '__main__':
    Demo().run()