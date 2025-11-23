import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

# Add this!
if current not in sys.path:
    sys.path.insert(0, current)

from dash import Input, Output, State, callback_context, no_update, ALL
import numpy as np
import base64
import tempfile
import importlib.util
from Utils import spectrogram, load_audio
from components.layouts.freq_fig import create_freq_figure
from components.layouts.spec_figure_layout import create_spec_figure

pyd_file = os.path.join(current, 'assets', 'build', 'lib.win-amd64-cpython-313', 'fft_module.cp313-win_amd64.pyd')
spec = importlib.util.spec_from_file_location("fft_module", pyd_file)
fft_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fft_module)


def register_Upload_signal(app):
    @app.callback(
        Output('signal-data-store', 'data'),
        Output('spectrogram-pre', 'figure'),
        Output('frequency-domain', 'figure'),
        Input('upload-signal', 'contents'),
        State('upload-signal', 'filename'),
        prevent_initial_call=True
    )
    def upload_signal(contents, filename):
        """Load and display uploaded signal"""
        if not contents:
            return no_update, no_update, no_update

        try:
            # Decode and save temporarily
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, filename)

            with open(temp_path, 'wb') as f:
                f.write(decoded)

            # Load audio
            signal, sr = load_audio(temp_path)

            # Convert stereo to mono
            if signal.ndim > 1:
                signal = signal.mean(axis=1)

            # Store data
            signal_data = {
                'samples': signal.tolist(),
                'signal': signal.tolist(),
                'sample_rate': int(sr),
                'filename': filename,

                'path':temp_path # Todo
            }

            # OPTIMIZATION: Limit FFT size for frequency plot
            max_fft_samples = 300032  # Adjust based on performance
            n_samples = min(len(signal), max_fft_samples)
            
            # Take power of 2 for FFT efficiency
            n_fft = 2 ** int(np.ceil(np.log2(n_samples)))
            
            # Prepare signal for FFT (pad to power of 2)
            signal_for_fft = np.zeros(n_fft, dtype=complex)
            signal_for_fft[:n_samples] = signal[:n_samples]
            
            # Compute FFT
            fft_result = fft_module.fft(signal_for_fft)
            
            # Only use positive frequencies
            N = len(fft_result)
            num_bins = N // 2 + 1
            frequencies = [k * sr / N for k in range(num_bins)]
            magnitudes = [abs(fft_result[k]) for k in range(num_bins)]

            # Create frequency figure (optimized)
            freq_fig = create_freq_figure(frequencies, magnitudes, use_db=True)

            # Create spectrogram (use full signal)
            f, t, Sxx = spectrogram(signal, sr, fft_module)
            spec_fig = create_spec_figure(f, t, Sxx)

            print(f"✓ Loaded: {filename} ({len(signal)} samples, {sr} Hz)")
            print(f"✓ FFT computed on {n_fft} samples for frequency plot")

            return signal_data, spec_fig, freq_fig
            # return signal_data,freq_fig

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return no_update, no_update, no_update