from dash import Input, Output, State, callback_context, no_update, ALL
import numpy as np
import plotly.graph_objs as go
import base64
import tempfile
import os

import sys
import importlib.util
from Utils import spectrogram, load_audio, save_audio_as_wav, audio_to_base64_uri
from components.layout_builder import create_slider
from Utils.load_mode import load_mode_config
from components.freq_fig import create_freq_figure
from components.spec_figure_layout import create_spec_figure
from components.time_domain_fig import create_time_figure

from modes.customized.sliders_layout_customized import create_customized_sliders_area
from modes.generic.sliders_layout_generic import create_generic_controls_area
            
current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

pyd_file = os.path.join(current, 'assets', 'build', 'lib.win-amd64-cpython-313', 'fft_module.cp313-win_amd64.pyd')
spec = importlib.util.spec_from_file_location("fft_module", pyd_file)
fft_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fft_module)


# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

def next_power_of_two_bitwise(n):
    if n == 0:
        return 1
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    n |= n >> 32  # only needed if working with big numbers
    return n + 1

def pad_to_next_power_of_two(data):
    current_size = len(data)
    target_size = next_power_of_two_bitwise(current_size)

    if target_size > current_size:
        # Pad with zeros
        data = data + [0] * (target_size - current_size)

    return data

# ========================================================================
# CALLBACKS
# ========================================================================
def register_main_callbacks(app):
    # ========================================================================
    # CALLBACK: Switch Mode
    # ========================================================================
    @app.callback(
        Output('mode-content-area', 'children'),
        Output('current-mode', 'data'),
        Input('mode-selector', 'value')
    )
    def switch_mode_content(mode):
        """Switches mode content (sliders or generic controls)"""

        slider_configs = load_mode_config(mode)
        
        if mode == 'generic':
            sliders_area = create_generic_controls_area()
            sliders = [create_slider(config) for config in slider_configs]
            content = create_generic_controls_area()

        else:
            sliders_area = create_customized_sliders_area()
            sliders = [create_slider(config) for config in slider_configs]
            content = create_customized_sliders_area()

        print(f"✓ Switched to {mode} mode")

        return content, mode

    # @app.callback(
    #     Output('signal-data-store', 'data'),
    #     # Output('spectrogram-pre', 'figure'),
    #     Output('frequency-domain', 'figure'),
    #     Input('upload-signal', 'contents'),
    #     State('upload-signal', 'filename'),
    #     prevent_initial_call=True
    # )
    # def upload_signal(contents, filename):
    #     """Load and display uploaded signal"""
    #     if not contents:
    #         return no_update, no_update, no_update

    #     try:
    #         # Decode and save temporarily
    #         content_type, content_string = contents.split(',')
    #         decoded = base64.b64decode(content_string)

    #         temp_dir = tempfile.gettempdir()
    #         temp_path = os.path.join(temp_dir, filename)

    #         with open(temp_path, 'wb') as f:
    #             f.write(decoded)

    #         # Load audio
    #         signal, sr = load_audio(temp_path)

    #         # Convert stereo to mono
    #         if signal.ndim > 1:
    #             signal = signal.mean(axis=1)

    #         # Store data - IMPORTANT: Use 'samples' key for cine viewer!
    #         signal_data = {
    #             'samples': signal.tolist(),  # Cine viewer needs 'samples'
    #             'signal': signal.tolist(),  # Keep for backward compatibility
    #             'sample_rate': int(sr),
    #             'filename': filename
    #         }

    #         # Create visualizations
    #         # f, t, Sxx = spectrogram(signal, sr)
    #         # f,t,Sxx = 0,0,0
    #         # spec_fig = create_spec_figure(f, t, Sxx)

    #         # Compute FFT for frequency domain
    #         signal_complex = signal.astype(complex)
    #         signal_complex = pad_to_next_power_of_two(signal_complex.tolist())
    #         fft_result = fft_module.fft(signal_complex)

    #         N = len(fft_result)
    #         num_bins = N // 2 + 1
    #         frequencies = [k * sr / N for k in range(num_bins)]
    #         magnitudes = [abs(fft_result[k]) for k in range(num_bins)]
    #         freq_fig = create_freq_figure(frequencies, magnitudes)

    #         print(f"✓ Loaded: {filename} ({len(signal)} samples, {sr} Hz)")

    #         # return (signal_data,spec_fig,freq_fig)
    #         return signal_data,freq_fig

    #     except Exception as e:
    #         print(f"✗ Error: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         return (no_update,
    #                 # no_update,
    #                 # no_update
    #                 )
    
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
                'filename': filename
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


    # ========================================================================
    # CALLBACK: Toggle Spectrograms
    # ========================================================================

    @app.callback(
        Output('spectrogram-pre-col', 'style'),
        Output('spectrogram-post-col', 'style'),
        Input('spectrogram-toggle', 'value')
    )
    def toggle_spectrograms(value):
        """Show/hide spectrograms"""
        if value and 'show' in value:
            # Show with proper width for side-by-side layout
            return {'width': '50%'}, {'width': '50%'}
        # Hide spectrograms
        return {'display': 'none'}, {'display': 'none'}

    # ========================================================================
    # CALLBACK: Play Audio
    # ========================================================================
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

    # ========================================================================
    # CALLBACK: Download
    # ========================================================================
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

    # ========================================================================
    # CALLBACK: Scale Toggle
    # ========================================================================
    @app.callback(
        Output('scale-linear', 'active'),
        Output('scale-audiogram', 'active'),
        Output('scale-linear', 'color'),
        Output('scale-audiogram', 'color'),
        Output('scale-linear', 'outline'),
        Output('scale-audiogram', 'outline'),
        Input('scale-linear', 'n_clicks'),
        Input('scale-audiogram', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_scale(linear, audio):
        """Toggle frequency scale with proper visual feedback"""
        ctx = callback_context
        
        if not ctx.triggered:
            # Default state: Linear active
            return True, False, "primary", "secondary", False, True
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'scale-linear':
            # Linear is active
            return True, False, "primary", "secondary", False, True
        else:
            # Audiogram is active
            return False, True, "secondary", "primary", True, False