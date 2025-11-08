from dash import Input, Output, State, callback_context, no_update
import numpy as np
import plotly.graph_objs as go
from Utils import process_signal
from Utils import spectrogram
from Utils import load_audio , save_audio_as_wav
from Utils import audio_to_base64_uri
import io
import base64


def register_customized_callbacks(app, frequency_maps):
    """
    Registers all callbacks for customized modes.

    Args:
        app: Dash app instance
        frequency_maps: Dictionary mapping slider IDs to frequency ranges
    """

    # ========================================================================
    # CALLBACK 1: Upload and Process Signal
    # ========================================================================
    @app.callback(
        Output('signal-data-store', 'data'),
        Output('time-domain-pre', 'figure'),
        Output('spectrogram-pre', 'figure'),
        Output('frequency-domain', 'figure'),
        Input('upload-signal', 'contents'),
        State('upload-signal', 'filename'),
        prevent_initial_call=True
    )
    def load_and_display_signal(contents, filename):
        """
        Loads uploaded signal and displays original time/frequency/spectrogram views.
        """
        if contents is None:
            return no_update, no_update, no_update, no_update

        # Load signal from uploaded file
        signal, sample_rate = load_audio(filename)

        # Store signal data
        signal_data = {
            'signal': signal.tolist(),
            'sample_rate': sample_rate,
            'duration': len(signal) / sample_rate,
            'filename': filename
        }

        # Compute FFT for frequency domain
        frequencies, magnitudes = process_signal(signal, sample_rate)

        # Create time domain figure
        time = np.arange(len(signal)) / sample_rate
        time_fig = create_time_domain_figure(time, signal, "Pre-Signal")

        # Create spectrogram figure
        spec_fig = create_spectrogram_figure(signal, sample_rate)

        # Create frequency domain figure
        freq_fig = create_frequency_domain_figure(frequencies, magnitudes)

        return signal_data, time_fig, spec_fig, freq_fig


    # ========================================================================
    # CALLBACK 2: Apply Equalizer (Main Processing)
    # ========================================================================
    @app.callback(
        Output('processed-signal-store', 'data'),
        Output('time-domain-post', 'figure'),
        Output('spectrogram-post', 'figure'),
        # Dynamic inputs based on sliders in frequency_maps
        [Input(slider_id, 'value') for slider_id in frequency_maps.keys()],
        State('signal-data-store', 'data'),
        State('scale-linear', 'active'),
        prevent_initial_call=True
    )
    def apply_equalizer(*args):
        """
        Applies frequency scaling based on slider values.
        This is the CORE processing function.
        """
        # Extract slider values (all inputs except last 2 states)
        slider_values = args[:-2]
        signal_data = args[-2]
        is_linear_scale = args[-1]

        if signal_data is None:
            return no_update, no_update, no_update

        # Reconstruct signal from stored data
        original_signal = np.array(signal_data['signal'])
        sample_rate = signal_data['sample_rate']

        # Compute FFT of original signal
        frequencies, fft_result = process_signal(list(original_signal), sample_rate)

        # Apply frequency scaling based on sliders
        modified_fft = apply_frequency_scaling(
            fft_result,
            frequencies,
            slider_values,
            frequency_maps
        )

        # Inverse FFT to get modified signal
        modified_signal = inverse_fft(modified_fft)

        # Make sure signal is real and same length
        modified_signal = np.real(modified_signal)[:len(original_signal)]

        # Normalize to prevent clipping
        max_val = np.max(np.abs(modified_signal))
        if max_val > 1.0:
            modified_signal = modified_signal / max_val

        # Store processed signal
        processed_data = {
            'signal': modified_signal.tolist(),
            'sample_rate': sample_rate
        }

        # Create visualizations
        time = np.arange(len(modified_signal)) / sample_rate
        time_fig = create_time_domain_figure(time, modified_signal, "Post-Signal")
        spec_fig = create_spectrogram_figure(modified_signal, sample_rate)

        return processed_data, time_fig, spec_fig


    # ========================================================================
    # CALLBACK 3: Update Frequency Domain Graph with Scale Toggle
    # ========================================================================
    @app.callback(
        Output('frequency-domain', 'figure', allow_duplicate=True),
        Input('scale-linear', 'n_clicks'),
        Input('scale-audiogram', 'n_clicks'),
        State('signal-data-store', 'data'),
        State('processed-signal-store', 'data'),
        prevent_initial_call=True
    )
    def toggle_frequency_scale(linear_clicks, audio_clicks, original_data, processed_data):
        """
        Toggles between linear and audiogram frequency scales.
        """
        if original_data is None:
            return no_update

        # Determine which scale to use
        ctx = callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        use_audiogram = (button_id == 'scale-audiogram')

        # Use processed signal if available, otherwise original
        signal_data = processed_data if processed_data else original_data
        signal = np.array(signal_data['signal'])
        sample_rate = signal_data['sample_rate']

        # Compute FFT
        frequencies, magnitudes = process_signal(list(signal), sample_rate)

        # Create figure with appropriate scale
        fig = create_frequency_domain_figure(
            frequencies,
            magnitudes,
            use_audiogram=use_audiogram
        )

        return fig


    # ========================================================================
    # CALLBACK 4: Toggle Scale Buttons
    # ========================================================================
    @app.callback(
        Output('scale-linear', 'active'),
        Output('scale-audiogram', 'active'),
        Input('scale-linear', 'n_clicks'),
        Input('scale-audiogram', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_scale_buttons(linear_clicks, audio_clicks):
        """Toggles active state of scale buttons."""
        ctx = callback_context
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'scale-linear':
            return True, False
        else:
            return False, True


    # ========================================================================
    # CALLBACK 5: Toggle Spectrogram Visibility
    # ========================================================================
    @app.callback(
        Output('spectrogram-pre-col', 'style'),
        Output('spectrogram-post-col', 'style'),
        Input('spectrogram-toggle', 'value'),
    )
    def toggle_spectrograms(toggle_value):
        """Shows/hides spectrogram columns."""
        if 'show' in toggle_value:
            return {'display': 'block'}, {'display': 'block'}
        else:
            return {'display': 'none'}, {'display': 'none'}


    # ========================================================================
    # CALLBACK 6: Play Audio Before
    # ========================================================================
    @app.callback(
        Output('audio-player-before', 'src'),
        Input('play-before', 'n_clicks'),
        State('signal-data-store', 'data'),
        prevent_initial_call=True
    )
    def play_audio_before(n_clicks, signal_data):
        """Converts original signal to playable audio."""
        if signal_data is None:
            return no_update

        signal = np.array(signal_data['signal'])
        sample_rate = signal_data['sample_rate']

        # Convert to base64 audio data URI
        audio_src = audio_to_base64_uri(signal, sample_rate)

        return audio_src


    # ========================================================================
    # CALLBACK 7: Play Audio After
    # ========================================================================
    @app.callback(
        Output('audio-player-after', 'src'),
        Input('play-after', 'n_clicks'),
        State('processed-signal-store', 'data'),
        prevent_initial_call=True
    )
    def play_audio_after(n_clicks, processed_data):
        """Converts processed signal to playable audio."""
        if processed_data is None:
            return no_update

        signal = np.array(processed_data['signal'])
        sample_rate = processed_data['sample_rate']

        audio_src = audio_to_base64_uri(signal, sample_rate)

        return audio_src


    # ========================================================================
    # NEW CALLBACK: Download Processed Audio File
    # ========================================================================
    @app.callback(
        Output('download-processed-audio', 'data'),
        Input('download-audio-btn', 'n_clicks'),
        State('processed-signal-store', 'data'),
        State('signal-data-store', 'data'),
        prevent_initial_call=True
    )
    def download_processed_audio(n_clicks, processed_data, original_data):
        """
        Downloads the processed audio as WAV file.
        Falls back to original if no processing has been done.
        """
        if processed_data is None and original_data is None:
            return no_update

        # Use processed signal if available, otherwise original
        signal_data = processed_data if processed_data else original_data
        signal = np.array(signal_data['signal'])
        sample_rate = signal_data['sample_rate']

        # Convert signal to WAV file bytes
        wav_bytes = save_audio_as_wav(signal, sample_rate)

        # Generate filename
        original_filename = original_data.get('filename', 'audio') if original_data else 'audio'
        base_name = original_filename.rsplit('.', 1)[0]
        new_filename = f"{base_name}_processed.wav"

        # Return as downloadable file
        return dict(
            content=wav_bytes,
            filename=new_filename,
            base64=True
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def apply_frequency_scaling(fft_result, frequencies, slider_values, frequency_maps):
    """
    Applies frequency scaling based on slider values and frequency maps.
    """
    modified_fft = fft_result.copy()

    # For each slider and its corresponding frequency ranges
    for slider_id, scale_value in zip(frequency_maps.keys(), slider_values):
        freq_ranges = frequency_maps[slider_id]

        # Apply scaling to each frequency range
        for start_freq, end_freq in freq_ranges:
            # Find indices in FFT that correspond to this range
            mask = (frequencies >= start_freq) & (frequencies <= end_freq)

            # Apply scaling
            modified_fft[mask] *= scale_value

    return modified_fft


def create_time_domain_figure(time, signal, title):
    """Creates time domain plot figure."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time,
        y=signal,
        mode='lines',
        line=dict(color='#00d9ff', width=1),
        name=title
    ))

    fig.update_layout(
        paper_bgcolor='#161821',
        plot_bgcolor='#161821',
        font=dict(color='#ffffff'),
        xaxis=dict(
            gridcolor='#2d3142',
            title='Time (s)',
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='#2d3142',
            title='Amplitude',
            showgrid=True
        ),
        margin=dict(l=50, r=20, t=30, b=40),
        height=200,
        showlegend=False
    )

    return fig


def create_spectrogram_figure(signal, sample_rate):
    """Creates spectrogram plot figure."""
    # Compute spectrogram using your utils function
    times, frequencies, spectrogram_graph = spectrogram(signal, sample_rate)

    # Convert to dB scale
    spectrogram_db = 10 * np.log10(spectrogram_graph + 1e-10)

    fig = go.Figure(data=go.Heatmap(
        z=spectrogram_db,
        x=times,
        y=frequencies,
        colorscale='Jet',
        showscale=False
    ))

    fig.update_layout(
        paper_bgcolor='#161821',
        plot_bgcolor='#161821',
        font=dict(color='#ffffff', size=8),
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        margin=dict(l=5, r=5, t=5, b=5),
        height=200
    )

    return fig


def create_frequency_domain_figure(frequencies, magnitudes, use_audiogram=False):
    """Creates frequency domain plot with optional audiogram scale."""

    if use_audiogram:
        # Audiogram uses logarithmic frequency scale
        xaxis_config = dict(
            type='log',
            gridcolor='#2d3142',
            title='Frequency (Hz)',
            showgrid=True
        )
    else:
        # Linear scale
        xaxis_config = dict(
            gridcolor='#2d3142',
            title='Frequency (Hz)',
            showgrid=True
        )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=frequencies,
        y=magnitudes,
        marker=dict(color='#00d9ff'),
        name='Magnitude'
    ))

    fig.update_layout(
        paper_bgcolor='#161821',
        plot_bgcolor='#161821',
        font=dict(color='#ffffff'),
        xaxis=xaxis_config,
        yaxis=dict(
            gridcolor='#2d3142',
            title='Magnitude',
            showgrid=True
        ),
        margin=dict(l=50, r=20, t=30, b=50),
        height=300,
        showlegend=False
    )

    return fig