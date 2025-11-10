"""
Customized Modes Callbacks
Handles: Musical Instruments, Animal Sounds, Human Voices
"""

from dash import Input, Output, State,no_update, ALL
import numpy as np
import os
import json

from Utils import spectrogram
from Utils.fft import ifft,time_to_frequency_linear
from components.layout_builder import create_slider
from components.main_callbacks import create_spec_figure,create_time_figure
from Utils.load_mode import load_mode_config
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

def load_frequency_map(mode):
    """Load frequency map for a customized mode"""
    
    # Define the modes that have dedicated files
    file_based_modes = ['Musical_Instruments', 'Animal_Sounds', 'Human_Voices']

    if mode in file_based_modes:
        # Dynamically create filename based on mode
        json_filename = f"Setting/{mode}_Frequency_Map.json"
        json_path = os.path.join(os.path.dirname(__file__), json_filename)
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Frequency map file not found at {json_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {json_path}")
            return {}
    
    elif mode == 'generic':
        # Generic mode has no sliders/map
        return {}
    else:
        # Handle other potential modes or error
        print(f"Warning: No frequency map defined for mode '{mode}'.")
        return {}

    freq_map = {}
    # Data is now the root object for that mode, access 'sliders' directly
    sliders = data.get('sliders', [])

    for slider in sliders:
        freq_map[slider['id']] = slider['frequency_ranges']

    return freq_map


def register_customized_callbacks(app):
    """Register callbacks for customized modes"""

    # ========================================================================
    # CALLBACK: Update Content
    # ========================================================================
    
    # @app.callback(
    #     Output('sliders-container', 'children'),
    #     Input('current-mode', 'data'),
    #     prevent_initial_call=True
    # )
    # def update_sliders(mode):
    #     """Updates sliders when mode changes"""
    #     # if mode == 'generic':
    #     #     return []
    #
    #     slider_configs = load_mode_config(mode)
    #     sliders = [create_slider(config) for config in slider_configs]
    #     return sliders
    #
    # ========================================================================
    # CALLBACK: Process Signal with Sliders (Customized Modes Only)
    # ========================================================================
    # @app.callback(
    #     Output('processed-signal-store', 'data'),
    #     Output('time-domain-post', 'figure'),
    #     Output('spectrogram-post', 'figure'),
    #     Input({'type': 'equalizer-slider', 'index': ALL}, 'value'),
    #     State('signal-data-store', 'data'),
    #     State('current-mode', 'data'),
    #     prevent_initial_call=True
    # )
    # def process_with_sliders(slider_values, signal_data, mode):
    #     """Apply equalization based on slider values (for customized modes)"""
    #
    #     # Skip if generic mode (has its own processing)
    #     if mode == 'generic' or not signal_data or not slider_values:
    #         return no_update, no_update, no_update
    #
    #     try:
    #         # Get signal
    #         print(len(signal_data))
    #         signal = np.array(signal_data['signal'])
    #         sr = signal_data['sample_rate']
    #
    #         # Get frequency map
    #         freq_map = load_frequency_map(mode)
    #
    #         # Process
    #         fft_result = time_to_frequency_linear(signal.tolist(), float(sr))
    #         modified_fft = apply_scaling(fft_result['full_fft'], freq_map, slider_values, sr, len(signal))
    #
    #         # Inverse FFT
    #         processed = ifft(modified_fft)
    #         processed = np.array([x.real for x in processed])[:len(signal)]
    #
    #         # Normalize
    #         max_val = np.max(np.abs(processed))
    #         if max_val > 1.0:
    #             processed /= max_val
    #
    #         # Store
    #         processed_data = {
    #             'signal': processed.tolist(),
    #             'sample_rate': sr
    #         }
    #
    #         # Visualize
    #         time = np.arange(len(processed)) / sr
    #         time_fig = create_time_figure(time, processed, "Processed Signal")
    #
    #         f, t, Sxx = spectrogram(processed, sr)
    #         spec_fig = create_spec_figure(f, t, Sxx)
    #
    #         print(f"✓ Processed with {len(slider_values)} sliders")
    #
    #         return processed_data, time_fig, spec_fig
    #
    #     except Exception as e:
    #         print(f"✗ Processing error: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         return no_update, no_update, no_update

    @app.callback(
        Output('processed-signal-store', 'data'),
        Output('spectrogram-post', 'figure'),
        Input({'type': 'equalizer-slider', 'index': ALL}, 'value'),
        State('signal-data-store', 'data'),
        State('current-mode', 'data'),
        prevent_initial_call=True
    )
    def process_with_sliders(slider_values, signal_data, mode):
        """Apply equalization based on slider values (for customized modes)"""

        # Skip if generic mode or no data
        if mode == 'generic' or not signal_data or not slider_values:
            return no_update, no_update

        try:
            # Get signal - check both 'samples' and 'signal' keys
            if 'samples' in signal_data:
                signal = np.array(signal_data['samples'])
            elif 'signal' in signal_data:
                signal = np.array(signal_data['signal'])
            else:
                return no_update, no_update

            sr = signal_data['sample_rate']

            # Get frequency map
            freq_map = load_frequency_map(mode)

            # Load FFT module
            import sys
            import importlib.util
            current = os.path.abspath(__file__)
            while not os.path.exists(os.path.join(current, 'assets')):
                current = os.path.dirname(current)
            pyd_file = os.path.join(current, 'assets', 'build', 'lib.win-amd64-cpython-313',
                                    'fft_module.cp313-win_amd64.pyd')
            spec = importlib.util.spec_from_file_location("fft_module", pyd_file)
            fft_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fft_module)

            # Process with FFT
            signal_complex = [complex(x, 0) for x in signal.tolist()]
            fft_result = fft_module.fft(signal_complex)

            # Apply frequency scaling
            modified_fft = apply_scaling(fft_result, freq_map, slider_values, sr, len(signal))

            # Inverse FFT
            processed_complex = fft_module.ifft(modified_fft)
            processed = np.array([x.real for x in processed_complex])[:len(signal)]

            # Normalize
            max_val = np.max(np.abs(processed))
            if max_val > 1.0:
                processed /= max_val

            # Store - IMPORTANT: Use 'samples' key for cine viewer!
            processed_data = {
                'samples': processed.tolist(),  # Cine viewer needs 'samples'
                'signal': processed.tolist(),  # Keep for backward compatibility
                'sample_rate': sr
            }

            # Create spectrogram
            f, t, Sxx = spectrogram(processed, sr)
            spec_fig = create_spec_figure(f, t, Sxx)

            print(f"✓ Processed with {len(slider_values)} sliders")

            return processed_data, spec_fig

        except Exception as e:
            print(f"✗ Processing error: {e}")
            import traceback
            traceback.print_exc()
            return no_update, no_update