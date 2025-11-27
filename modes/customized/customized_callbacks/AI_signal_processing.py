import os
import numpy as np
import soundfile as sf
from dash import Input, Output, State, no_update
import importlib.util

from Utils import spectrogram
from components.layouts.spec_figure_layout import create_spec_figure
from components.layouts.freq_fig import create_freq_figure

# Keep the optimization for module loading
_FFT_MODULE_CACHE = None


def _get_fft_module():
    global _FFT_MODULE_CACHE
    if _FFT_MODULE_CACHE is not None:
        return _FFT_MODULE_CACHE
    try:
        current = os.path.abspath(__file__)
        while not os.path.exists(os.path.join(current, 'assets')):
            parent = os.path.dirname(current)
            if parent == current: raise FileNotFoundError("Assets not found")
            current = parent
        pyd_file = os.path.join(current, 'assets', 'build', 'lib.win-amd64-cpython-313',
                                'fft_module.cp313-win_amd64.pyd')
        spec = importlib.util.spec_from_file_location("fft_module", pyd_file)
        fft_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fft_module)
        _FFT_MODULE_CACHE = fft_module
        return fft_module
    except:
        return None


def process_ai_output(audio_src):
    if not audio_src: return no_update, no_update, no_update

    try:
        filename = audio_src.split('/')[-1].split('?')[0]
        filepath = os.path.join(os.getcwd(), 'static', filename)
        if not os.path.exists(filepath): return no_update, no_update, no_update

        signal, sr = sf.read(filepath, always_2d=False)
        if signal.ndim > 1: signal = signal.mean(axis=1)

        processed_data = {
            'sample_rate': int(sr),
            'duration': len(signal) / sr,
            'samples_preview': signal[::100].tolist()
        }

        fft_module = _get_fft_module()
        if not fft_module: return processed_data, no_update, no_update

        f, t, Sxx = spectrogram(signal, sr, fft_module)
        spec_fig = create_spec_figure(f, t, Sxx)

        max_fft_samples = 300032
        n_samples = min(len(signal), max_fft_samples)
        n_fft = 2 ** int(np.ceil(np.log2(n_samples)))
        signal_for_fft = np.zeros(n_fft, dtype=complex)
        signal_for_fft[:n_samples] = signal[:n_samples]
        fft_result = fft_module.fft(signal_for_fft)

        N = len(fft_result)
        num_bins = N // 2 + 1
        frequencies = np.linspace(0, sr / 2, num_bins)
        magnitudes = np.abs(fft_result[:num_bins])
        freq_fig = create_freq_figure(frequencies, magnitudes, use_db=True)

        return processed_data, spec_fig, freq_fig

    except Exception as e:
        print(f"Error: {e}")
        return no_update, no_update, no_update


def register_ai_signal_processing(app):
    """
    Registers TWO SEPARATE callbacks.
    """

    # 1. Callback for the Standard AI Player (Musical Mode)
    @app.callback(
        Output('ai-processed-signal-store', 'data'),
        Output('ai-spectrogram', 'figure'),
        Output('ai-frequency-domain', 'figure'),
        Input('ai-audio-player', 'src'),
        # State('signal-data-store', 'data'),
        prevent_initial_call=True
    )
    def update_musical_ai(audio_src):
        return process_ai_output(audio_src)

    # 2. Callback for the Human AI Player (Voice Mode)
    @app.callback(
        Output('human-ai-processed-signal-store', 'data', allow_duplicate=True),
        Output('ai-spectrogram', 'figure', allow_duplicate=True),
        Output('ai-frequency-domain', 'figure', allow_duplicate=True),
        Input('human-ai-audio-player', 'src'),
        # State('signal-data-store', 'data'),
        prevent_initial_call=True
    )
    def update_human_ai(audio_src):
        return process_ai_output(audio_src)

