"""
Customized Modes Callbacks
Handles: Musical Instruments, Animal Sounds, Human Voices
"""

import os
import sys
import importlib
import importlib.util
import copy

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

if current not in sys.path:
    sys.path.insert(0, current)

from dash import Input, Output, State, no_update, ALL
from dash.exceptions import PreventUpdate
import numpy as np

from Utils import spectrogram
from components.layouts.spec_figure_layout import create_spec_figure
from components.layouts.freq_fig import create_freq_figure
from Utils.load_mode import load_mode_config

from modes.generic.callbacks import _get_fft_module,_pad_signal_to_power_of_two,_build_cache_key,_spectrogram_subset,_create_frequency_figure

# ============================================================================
# Global Variables
# ============================================================================

_FFT_MODULE = None
_FFT_CACHE = {}
_PYD_RELATIVE = os.path.join(
    "assets", "build", "lib.win-amd64-cpython-313", "fft_module.cp313-win_amd64.pyd"
)
_MAX_SPECTROGRAM_SAMPLES = 262_144

# ============================================================================
# Helper Functions
# ============================================================================
def _get_cached_fft(signal_data, fft_module, mode):
    """Get or compute cached FFT for signal"""
    key = f"{mode}-{_build_cache_key(signal_data)}"
    cached = _FFT_CACHE.get(key)
    if cached:
        return cached

    # Get original signal
    original_signal = np.array(
        signal_data.get("samples") or signal_data.get("signal"), dtype=float
    )
    
    # Pad signal
    padded_signal, fft_len = _pad_signal_to_power_of_two(original_signal)
    if fft_len == 0:
        cache_entry = {
            "key": key,
            "original_signal": original_signal,
            "padded_signal": padded_signal,
            "base_fft": np.array([]),
            "freq_bins": np.array([]),
            "original_spec_fig": None,
            "original_freq_fig": None,
        }
        _FFT_CACHE[key] = cache_entry
        return cache_entry

    # Compute FFT
    signal_complex = [complex(x, 0) for x in padded_signal.tolist()]
    fft_result = np.array(fft_module.fft(signal_complex), dtype=complex)
    
    # Compute frequency bins
    sample_rate = signal_data["sample_rate"]
    freq_bins = np.abs(np.fft.fftfreq(len(fft_result), 1 / sample_rate))
    
    # Create original visualizations
    f, t, Sxx = _spectrogram_subset(original_signal, sample_rate, fft_module)
    original_spec_fig = create_spec_figure(f, t, Sxx)
    original_freq_fig = _create_frequency_figure(fft_result, sample_rate, allow_none=True)

    cache_entry = {
        "key": key,
        "original_signal": original_signal,
        "padded_signal": padded_signal,
        "base_fft": fft_result,
        "freq_bins": freq_bins,
        "original_spec_fig": original_spec_fig,
        "original_freq_fig": original_freq_fig,
    }
    _FFT_CACHE[key] = cache_entry
    return cache_entry


def load_frequency_map(mode):
    """Load frequency map for a customized mode"""
    sliders = load_mode_config(mode)
    freq_map = {}

    for slider in sliders:
        freq_map[slider['id']] = slider['frequency_ranges']

    return freq_map


def _apply_bands(base_fft, freq_bins, freq_map, slider_values):
    """Apply frequency scaling based on slider values"""
    if not slider_values:
        return np.array(base_fft, dtype=complex, copy=True)

    fft_array = np.array(base_fft, dtype=complex, copy=True)
    slider_ids = list(freq_map.keys())

    for idx, slider_id in enumerate(slider_ids):
        if idx >= len(slider_values):
            break

        gain = slider_values[idx]
        if gain is None or np.isclose(gain, 1.0):
            continue

        ranges = freq_map.get(slider_id, [])
        for band in ranges:
            if not band or len(band) < 2:
                continue
            low, high = sorted([float(band[0]), float(band[1])])
            mask = (freq_bins >= low) & (freq_bins <= high)
            if not np.any(mask):
                continue
            fft_array[mask] *= gain

    return fft_array


# ============================================================================
# Callback Registration
# ============================================================================

def register_customized_callbacks(app):
    """Register callbacks for customized modes"""

    @app.callback(
        Output('processed-signal-store', 'data'),
        Output('spectrogram-post', 'figure'),
        Output('frequency-domain', 'figure', allow_duplicate=True),
        Input({'type': 'equalizer-slider', 'index': ALL}, 'value'),
        State('signal-data-store', 'data'),
        State('current-mode', 'data'),
        prevent_initial_call=True
    )
    def process_with_sliders(slider_values, signal_data, mode):
        """Apply equalization based on slider values (for customized modes)"""

        # Skip if generic mode or no data
        if mode == 'generic' or not signal_data or not slider_values:
            raise PreventUpdate

        try:
            # Get FFT module
            fft_module = _get_fft_module()
            
            # Get cached FFT computation
            cache_entry = _get_cached_fft(signal_data, fft_module, mode)
            original_signal = cache_entry["original_signal"]
            base_fft = cache_entry["base_fft"]
            freq_bins = cache_entry["freq_bins"]
            original_spec_fig = cache_entry.get("original_spec_fig")
            original_freq_fig = cache_entry.get("original_freq_fig")
            sample_rate = signal_data["sample_rate"]

            # Get frequency map for current mode
            freq_map = load_frequency_map(mode)

            # Check if any sliders are not at default (1.0)
            active_sliders = [val for val in slider_values if not np.isclose(val, 1.0)]

            if base_fft.size == 0 or not active_sliders:
                # No processing needed, use original
                processed = original_signal
                modified_fft = base_fft
            else:
                # Apply frequency scaling
                modified_fft = _apply_bands(base_fft, freq_bins, freq_map, slider_values)
                
                # Inverse FFT
                processed_complex = fft_module.ifft(modified_fft.tolist())
                processed = np.array([x.real for x in processed_complex])[:len(original_signal)]

            # Normalize if needed
            if processed.size:
                max_val = np.max(np.abs(processed))
                if max_val > 1.0:
                    processed = processed * (0.99 / max_val)

            # Store processed signal
            processed_list = processed.astype(float).tolist()
            processed_data = {
                'samples': processed_list,
                'signal': processed_list,
                'sample_rate': sample_rate
            }

            # Create visualizations
            if active_sliders:
                # Recompute visualizations for modified signal
                f, t, Sxx = _spectrogram_subset(processed, sample_rate, fft_module)
                spec_fig = create_spec_figure(f, t, Sxx)
                freq_fig = _create_frequency_figure(modified_fft, sample_rate)
            else:
                # Use cached original visualizations
                spec_fig = copy.deepcopy(original_spec_fig) if original_spec_fig else create_spec_figure(*_spectrogram_subset(original_signal, sample_rate, fft_module))
                freq_fig = copy.deepcopy(original_freq_fig) if original_freq_fig else _create_frequency_figure(base_fft, sample_rate)

            print(f"✓ Processed with {len(slider_values)} sliders ({len(active_sliders)} active)")

            return processed_data, spec_fig, freq_fig

        except Exception as e:
            print(f"✗ Processing error: {e}")
            import traceback
            traceback.print_exc()
            raise PreventUpdate