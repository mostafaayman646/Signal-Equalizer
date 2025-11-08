"""
Customized Modes Callbacks
Handles: Musical Instruments, Animal Sounds, Human Voices
"""

from dash import Input, Output, State, callback_context, no_update, ALL
import numpy as np
import plotly.graph_objs as go
import base64
import tempfile
import os
import json

from Utils import process_signal, spectrogram, load_audio, save_audio_as_wav, audio_to_base64_uri
from Utils.fft import ifft
from components.layout_builder import load_mode_config, create_slider, create_customized_sliders_area


def load_frequency_map(mode):
    """Load frequency map for a customized mode"""
    json_path = os.path.join(os.path.dirname(__file__), 'frequency_maps.json')

    with open(json_path, 'r') as f:
        data = json.load(f)

    freq_map = {}
    sliders = data['modes'].get(mode, {}).get('sliders', [])

    for slider in sliders:
        freq_map[slider['id']] = slider['frequency_ranges']

    return freq_map


def register_customized_callbacks(app):
    """Register callbacks for customized modes"""

    # ========================================================================
    # CALLBACK: Switch Mode and Update Content
    # ========================================================================
    @app.callback(
        Output('mode-content-area', 'children'),
        Output('current-mode', 'data'),
        Input('mode-selector', 'value')
    )
    def switch_mode_content(mode):
        """Switches mode content (sliders or generic controls)"""

        # if mode == 'generic':
        #     from components.layout_builder import create_generic_controls_area
        #     return create_generic_controls_area(), mode

        # For customized modes, create sliders
        slider_configs = load_mode_config(mode)
        sliders_area = create_customized_sliders_area()
        sliders = [create_slider(config) for config in slider_configs]

        # Update sliders container

        content = create_customized_sliders_area()

        print(f"✓ Switched to {mode} mode")

        return content, mode

    # Secondary callback to populate sliders
    @app.callback(
        Output('sliders-container', 'children'),
        Input('current-mode', 'data'),
        prevent_initial_call=True
    )
    def update_sliders(mode):
        """Updates sliders when mode changes"""
        if mode == 'generic':
            return []

        slider_configs = load_mode_config(mode)
        sliders = [create_slider(config) for config in slider_configs]
        return sliders

    # ========================================================================
    # CALLBACK: Upload Signal
    # ========================================================================
    @app.callback(
        Output('signal-data-store', 'data'),
        # Output('time-domain-pre', 'figure'),
        # Output('spectrogram-pre', 'figure'),
        # Output('frequency-domain', 'figure'),
        Input('upload-signal', 'contents'),
        State('upload-signal', 'filename'),
        prevent_initial_call=True
    )
    def upload_signal(contents, filename):
        """Load and display uploaded signal"""
        if not contents:
            return no_update, no_update, no_update, no_update

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
                'signal': signal.tolist(),
                'sample_rate': int(sr),
                'filename': filename
            }

            # Create visualizations
            # fft_result = process_signal(signal.tolist(), float(sr))
            # time = np.arange(len(signal)) / sr

            # time_fig = create_time_figure(time, signal, "Original Signal")

            # f, t, Sxx = spectrogram(signal, sr)
            # spec_fig = create_spec_figure(f, t, Sxx)

            # freq_fig = create_freq_figure(fft_result['frequencies'], fft_result['magnitude'])

            print(f"✓ Loaded: {filename} ({len(signal)} samples, {sr} Hz)")
            # print(len(signal_data))
            # return (signal_data,
            #         # time_fig,
            #         # spec_fig,
            #         # freq_fig
            # )
            return signal_data

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return no_update, no_update , no_update,no_update

    # ========================================================================
    # CALLBACK: Process Signal with Sliders (Customized Modes Only)
    # ========================================================================
    @app.callback(
        Output('processed-signal-store', 'data'),
        Output('time-domain-post', 'figure'),
        Output('spectrogram-post', 'figure'),
        Input({'type': 'equalizer-slider', 'index': ALL}, 'value'),
        State('signal-data-store', 'data'),
        State('current-mode', 'data'),
        prevent_initial_call=True
    )
    def process_with_sliders(slider_values, signal_data, mode):
        """Apply equalization based on slider values (for customized modes)"""

        # Skip if generic mode (has its own processing)
        if mode == 'generic' or not signal_data or not slider_values:
            return no_update, no_update, no_update

        try:
            # Get signal
            print(len(signal_data))
            signal = np.array(signal_data['signal'])
            sr = signal_data['sample_rate']

            # Get frequency map
            freq_map = load_frequency_map(mode)

            # Process
            fft_result = process_signal(signal.tolist(), float(sr))
            modified_fft = apply_scaling(fft_result['full_fft'], freq_map, slider_values, sr, len(signal))

            # Inverse FFT
            processed = ifft(modified_fft)
            processed = np.array([x.real for x in processed])[:len(signal)]

            # Normalize
            max_val = np.max(np.abs(processed))
            if max_val > 1.0:
                processed /= max_val

            # Store
            processed_data = {
                'signal': processed.tolist(),
                'sample_rate': sr
            }

            # Visualize
            time = np.arange(len(processed)) / sr
            time_fig = create_time_figure(time, processed, "Processed Signal")

            f, t, Sxx = spectrogram(processed, sr)
            spec_fig = create_spec_figure(f, t, Sxx)

            print(f"✓ Processed with {len(slider_values)} sliders")

            return processed_data, time_fig, spec_fig

        except Exception as e:
            print(f"✗ Processing error: {e}")
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
            return {}, {}
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
        Input('scale-linear', 'n_clicks'),
        Input('scale-audiogram', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_scale(linear, audio):
        """Toggle frequency scale"""
        ctx = callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'scale-linear':
            return True, False
        return False, True


# ============================================================================
# Helper Functions
# ============================================================================

def apply_scaling(fft_data, freq_map, slider_values, sr, length):
    """Apply frequency scaling"""
    full_fft = list(fft_data)
    full_freq = np.fft.fftfreq(length, 1 / sr)
    full_freq = np.abs(full_freq)

    slider_ids = list(freq_map.keys())

    for idx, slider_id in enumerate(slider_ids):
        if idx >= len(slider_values):
            break

        scale = slider_values[idx]
        if scale is None:
            continue

        for start_f, end_f in freq_map[slider_id]:
            for i in range(len(full_fft)):
                if start_f <= full_freq[i] <= end_f:
                    full_fft[i] *= scale

    return full_fft


def create_time_figure(time, signal, title):
    """Create time domain figure"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time, y=signal, mode='lines', line=dict(color='#00d9ff', width=1)))
    fig.update_layout(
        paper_bgcolor='#161821', plot_bgcolor='#161821',
        font=dict(color='#ffffff'),
        xaxis=dict(gridcolor='#2d3142', title='Time (s)'),
        yaxis=dict(gridcolor='#2d3142', title='Amplitude'),
        margin=dict(l=40, r=20, t=20, b=40),
        height=200, showlegend=False
    )
    return fig


def create_spec_figure(f, t, Sxx):
    """Create spectrogram figure"""
    Sxx_db = 10 * np.log10(Sxx + 1e-10)
    fig = go.Figure(data=go.Heatmap(z=Sxx_db, x=t, y=f, colorscale='Jet', showscale=False))
    fig.update_layout(
        paper_bgcolor='#161821', plot_bgcolor='#161821',
        font=dict(color='#ffffff', size=8),
        xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False),
        margin=dict(l=5, r=5, t=5, b=5), height=200
    )
    return fig


def create_freq_figure(freq, mag):
    """Create frequency domain figure"""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=freq, y=mag, marker=dict(color='#00d9ff')))
    fig.update_layout(
        paper_bgcolor='#161821', plot_bgcolor='#161821',
        font=dict(color='#ffffff'),
        xaxis=dict(gridcolor='#2d3142', title='Frequency (Hz)'),
        yaxis=dict(gridcolor='#2d3142', title='Magnitude'),
        margin=dict(l=40, r=20, t=20, b=40),
        height=300, showlegend=False
    )
    return fig