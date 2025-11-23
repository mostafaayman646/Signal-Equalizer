import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

# Add this!
if current not in sys.path:
    sys.path.insert(0, current)

from components.callbacks.Upload_signal import register_Upload_signal
from components.callbacks.NavBar_Mode_Switch import register_mode_switch
from components.callbacks.Toggle_spectogram import register_Toggle_spectogram
from components.callbacks.PlayAudio import register_PlayAudio
from components.callbacks.Download_Audio import register_Download_audio
from components.callbacks.Scale_toggle import register_Scale_toggle

__all__ = ['register_Upload_signal','register_mode_switch','register_PlayAudio','register_Toggle_spectogram',
           'register_Download_audio','register_Scale_toggle']