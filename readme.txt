I want to try to investigate why buildozer is not working properly with pyaudio.
For that i :
1. in virtual environment omnienv install kivy project.

python -m pip install --user kivy
After that installed audiostream:

2. pip3 install git+https://github.com/kivy/audiostream.git - didn't work, wasn't able to import audiostream
instead did the following:
git clone https://github.com/kivy/audiostream.git, go to the folder with setup.py and run:
 sudo python setup.py install.
3. Now need to test if everything is working by making a project from audiostream/examples:

import time
import wave
from audiostream import get_input

frames = []


def mic_callback(buf):
    print('got', len(buf))
    frames.append(buf)

# get the default audio input (mic on most cases)


mic = get_input(callback=mic_callback)
mic.start()

time.sleep(5)

mic.stop()

wf = wave.open("test.wav", 'wb')
wf.setnchannels(mic.channels)
wf.setsampwidth(2)
wf.setframerate(mic.rate)
wf.writeframes(b''.join(frames))
wf.close()

4. When this code runs on desktop it gives:
audiostream.core.get_input
Exception: Unsupported platform

5. Want to try build project above for android (buildozer). Here is quote why pyaudio is not working for android:
At the end of the day, you are going to need to build an executable (or multiple executables) for the platforms you are targeting.
 This might involve Buildozer (Android), PyInstaller (Windows), or other tools. The main thing to be careful of is libraries that
 have platform-specific dependencies such as compiled C extensions. For instance, PyAudio doesn’t support Android as far as I can tell.
 You would need to use Android specific libraries for audio there. Are you sure the Kivy audio library doesn’t provide any hat you need?
  If you stick to pure python libs you won’t have any issue, and even if you do need such dependencies you can make it work,
  it just might be more difficult. For instance if you need a compiled Linux dependency for Android and you are developing on Windows or OSX,
  it’s going to be tricky. I would maybe try to get the executable build working soon ( even if it’s just a HelloWorld app that calls PyAudio
   to play a simple sound file) and running on your target platform just to make sure the entire toolchain is working for what you need.