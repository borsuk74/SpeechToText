#google code, which uses kivy and audiostream,
#should record from microphone into file.
#Need to make sure that I know how to deploy such applications.
from kivy.app import App
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
#import audiostream as sd
import time
import wave
from audiostream import get_input

class Demo(App):
    def set_background_color(self):
        with self.label.canvas.before:
            Color(0.5, 0.0, 0.5)
            Rectangle(size=Window.size)

    def _resize_handler(self,obj,size):
        self.set_background_color()

    def mic_callback(self,buf):
        #print('got', len(buf))
        self.frames.append(buf)

    def on_start(self):

        self._frames = []
        mic = get_input(callback=self.mic_callback)
        mic.start()
        time.sleep(10)
        mic.stop()

        wf = wave.open("test.wav", 'wb')
        wf.setnchannels(mic.channels)
        wf.setsampwidth(2)
        wf.setframerate(mic.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        symbols = 'Recording completed!'
        #for m in dir(sd):
            #symbols += m + '\n'
        self.label.text = symbols

    def build(self):
        Window.bind(size=self._resize_handler)
        self.label = Label(text = 'Greetings Earthlings')
        self.set_background_color()
        return self.label

if __name__ == '__main__':
    Demo().run()
