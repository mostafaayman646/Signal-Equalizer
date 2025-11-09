from dash import Input, Output, State, callback_context, no_update, ALL
import numpy as np
import plotly.graph_objs as go
import base64
import tempfile
import os

from Utils import spectrogram, load_audio, save_audio_as_wav, audio_to_base64_uri
from components.layout_builder import load_mode_config, create_slider, create_customized_sliders_area

# ========================================================================
# HELPER FUNCTIONS
# ========================================================================
def create_spec_figure(f, t, Sxx):#Main callbacks -----------------------------------------------------------------
    """Create spectrogram figure"""
    # Sxx_db = 10 * np.log10(Sxx + 1e-10)
    fig = go.Figure(data=go.Heatmap(z=Sxx, x=t, y=f, colorscale='Viridis'))
    fig.update_layout(
        paper_bgcolor='#161821', plot_bgcolor='#161821',
        font=dict(color='#ffffff', size=8),
        xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False),
        margin=dict(l=5, r=5, t=5, b=5), height = 300, width = 325
    )
    return fig

def create_time_figure(time, signal, title):#Main callbacks -----------------------------------------------------------------
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

def create_freq_figure(freq, mag):#Main callbacks -----------------------------------------------------------------
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
            # fft_result = time_to_frequency_linear(signal.tolist(), float(sr))
            # time = np.arange(len(signal)) / sr

            # time_fig = create_time_figure(time, signal, "Original Signal")

            # f, t, Sxx = spectrogram(signal, sr)
            # spec_fig = create_spec_figure(f, t, Sxx)

            # freq_fig = create_freq_figure(fft_result['frequencies'], fft_result['magnitude'])

            # print(f"✓ Loaded: {filename} ({len(signal)} samples, {sr} Hz)")
            # print(len(signal_data))
            # return (signal_data,
            #         # time_fig,
            #         spec_fig,
            #         # freq_fig
            # )
            return signal_data

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return no_update, no_update , no_update,no_update
    
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