import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

# Add this!
if current not in sys.path:
    sys.path.insert(0, current)

from dash import Input, Output, State, no_update, ALL
import numpy as np
import tempfile
import base64

from Utils import save_audio_as_wav

def register_Download_audio(app):
    @app.callback(
        Output('download-processed-audio', 'data'),
        Input('download-audio-btn', 'n_clicks'),
        State('processed-signal-store', 'data'),
        State('signal-data-store', 'data'),
        prevent_initial_call=True
    )
    def download_audio(n, processed, original):
        """Download processed audio"""
        if not processed and not original:
            return no_update

        data = processed if processed else original
        signal = np.array(data['signal'])
        sr = data['sample_rate']

        filename = original.get('filename', 'audio') if original else 'audio'
        output_name = f"{filename.rsplit('.', 1)[0]}_processed.wav"

        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, output_name)
        save_audio_as_wav(signal, sr, temp_path, normalize=True)

        with open(temp_path, 'rb') as f:
            wav_bytes = f.read()

        encoded = base64.b64encode(wav_bytes).decode()

        return dict(content=encoded, filename=output_name, base64=True)