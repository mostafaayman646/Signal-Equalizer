import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

# Add this!
if current not in sys.path:
    sys.path.insert(0, current)

from dash import Input, Output, State, no_update, ALL
from Utils import audio_to_base64_uri
import numpy as np

def register_PlayAudio(app):
    @app.callback(
    Output('audio-player-before', 'src'),
    Input('load-before', 'n_clicks'),
    State('signal-data-store', 'data'),
    prevent_initial_call=True
    )
    def play_original(n, data):
        """Play original signal"""
        if not data:
            return no_update

        signal = np.array(data['signal'])
        sr = data['sample_rate']
        return audio_to_base64_uri(signal, sr, normalize=True)

    @app.callback(
        Output('audio-player-after', 'src'),
        Input('load-after', 'n_clicks'),
        State('processed-signal-store', 'data'),
        prevent_initial_call=True
    )
    def play_processed(n, data):
        """Play processed signal"""
        if not data:
            return no_update

        signal = np.array(data['signal'])
        sr = data['sample_rate']
        return audio_to_base64_uri(signal, sr, normalize=True)