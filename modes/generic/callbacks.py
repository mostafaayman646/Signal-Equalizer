import importlib
import importlib.util
import os
import sys
import uuid
import json
import copy

import numpy as np
import dash_bootstrap_components as dbc
from dash import Input, Output, State, ALL, ctx, no_update, html, dcc
from dash.exceptions import PreventUpdate

from components.layouts.freq_fig import create_freq_figure
from components.layouts.spec_figure_layout import create_spec_figure
from modes.generic.sliders_layout_generic import create_generic_controls_area
from Utils import spectrogram, audio_to_base64_uri

_FFT_MODULE = None
_DEFAULT_HELPER = "Waiting for clicks…"
_FFT_CACHE = {}
_PYD_RELATIVE = os.path.join(
    "assets", "build", "lib.win-amd64-cpython-313", "fft_module.cp313-win_amd64.pyd"
)
_MAX_SPECTROGRAM_SAMPLES = 262_144
_GENERIC_JSON_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "Setting", "generic_Frequency_Map.json"
)
_GENERIC_JSON_PATH = os.path.abspath(_GENERIC_JSON_PATH)


def _get_fft_module():
    global _FFT_MODULE
    if _FFT_MODULE is not None:
        return _FFT_MODULE

    try:
        module = sys.modules.get("fft_module")
        if module is None:
            module = importlib.import_module("fft_module")
    except ModuleNotFoundError:
        current = os.path.abspath(__file__)
        while not os.path.exists(os.path.join(current, "assets")):
            current = os.path.dirname(current)
        pyd_path = os.path.join(current, _PYD_RELATIVE)
        spec = importlib.util.spec_from_file_location("fft_module", pyd_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules["fft_module"] = module

    _FFT_MODULE = module
    return module


def _format_freq(value):
    if value is None:
        return "—"
    value = float(value)
    if value >= 1000:
        return f"{value/1000:.1f}k"
    if value.is_integer():
        return f"{int(value)}"
    return f"{value:.1f}"


def _render_empty_state():
    return html.Div(
        [
            html.Div(
                "No custom bands yet.",
                style={"fontSize": "0.9rem", "fontWeight": "600"},
            ),
            html.Div(
                "Click two points on the frequency plot to create your first slider.",
                style={"fontSize": "0.8rem", "color": "#a0a4b8"},
            ),
        ],
        style={
            "textAlign": "center",
            "color": "#fff",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "center",
            "minHeight": "180px",
            "width": "100%",
        },
    )


def _build_slider_card(slider):
    slider_id = slider["id"]
    label = slider.get("label") or "Custom Band"
    low, high = slider.get("range", [0, 0])
    gain = slider.get("gain", 1.0)
    range_text = f"{_format_freq(low)} – {_format_freq(high)} Hz"

    return html.Div(
        [
            dcc.Slider(
                id={"type": "generic-slider", "index": slider_id},
                min=0,
                max=2,
                step=0.1,
                value=gain,
                marks={0: "0x", 1: "1x", 2: "2x"},
                tooltip={"placement": "right"},
                vertical=True,
                verticalHeight=200,
            ),
            html.Div(
                label,
                style={
                    "color": "#fff",
                    "fontWeight": "600",
                    "fontSize": "0.85rem",
                    "textAlign": "center",
                },
            ),
            html.Div(
                range_text,
                style={
                    "color": "#a0a4b8",
                    "fontSize": "0.75rem",
                    "textAlign": "center",
                },
            ),
            dbc.Button(
                "Delete",
                id={"type": "generic-delete-slider", "index": slider_id},
                color="danger",
                outline=True,
                size="sm",
                className="mt-1",
            ),
        ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "gap": "0.35rem",
            "padding": "0 1rem",
            "minWidth": "110px",
        },
    )


def _apply_bands(base_fft, freq_bins, sliders):
    if not sliders:
        return np.array(base_fft, dtype=complex, copy=True)

    fft_array = np.array(base_fft, dtype=complex, copy=True)
    for slider in sliders:
        gain = slider.get("gain", 1.0)
        if gain is None or np.isclose(gain, 1.0):
            continue

        ranges = slider.get("frequency_ranges")
        if not ranges and slider.get("range"):
            ranges = [slider["range"]]

        for band in ranges or []:
            if not band or len(band) < 2:
                continue
            low, high = sorted([float(band[0]), float(band[1])])
            mask = (freq_bins >= low) & (freq_bins <= high)
            if not np.any(mask):
                continue
            fft_array[mask] *= gain

    return fft_array


def _pad_signal_to_power_of_two(signal):
    length = len(signal)
    if length == 0:
        return np.array([], dtype=float), 0
    exponent = int(np.ceil(np.log2(max(length, 8))))
    fft_len = 1 << exponent
    padded = np.zeros(fft_len, dtype=float)
    padded[:length] = signal
    return padded, fft_len


def _fft_to_freq_arrays(fft_result, sample_rate):
    if fft_result is None:
        return [], []
    if isinstance(fft_result, np.ndarray) and fft_result.size == 0:
        return [], []
    if isinstance(fft_result, list) and len(fft_result) == 0:
        return [], []
    N = len(fft_result)
    if N == 0:
        return [], []
    num_bins = N // 2 + 1
    frequencies = [k * sample_rate / N for k in range(num_bins)]
    magnitudes = [abs(fft_result[k]) for k in range(num_bins)]
    return frequencies, magnitudes


def _create_frequency_figure(fft_result, sample_rate, allow_none=False):
    frequencies, magnitudes = _fft_to_freq_arrays(fft_result, sample_rate)
    if not frequencies:
        return None if allow_none else no_update
    return create_freq_figure(frequencies, magnitudes, use_db=True)


def _spectrogram_subset(signal, sample_rate, fft_module):
    if signal.size <= _MAX_SPECTROGRAM_SAMPLES:
        subset = signal
    else:
        subset = signal[:_MAX_SPECTROGRAM_SAMPLES]
    return spectrogram(subset, sample_rate, fft_module)


def _build_cache_key(signal_data):
    path = signal_data.get("path")
    if path and os.path.exists(path):
        try:
            modified = os.path.getmtime(path)
        except OSError:
            modified = 0
        length = len(signal_data.get("samples", []))
        return f"{path}-{modified}-{length}"
    return f"{signal_data.get('filename')}-{len(signal_data.get('samples', []))}"


def _get_cached_fft(signal_data, fft_module):
    key = _build_cache_key(signal_data)
    cached = _FFT_CACHE.get(key)
    if cached:
        return cached

    original_signal = np.array(
        signal_data.get("samples") or signal_data.get("signal"), dtype=float
    )
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

    signal_complex = [complex(x, 0) for x in padded_signal.tolist()]
    fft_result = np.array(fft_module.fft(signal_complex), dtype=complex)
    sample_rate = signal_data["sample_rate"]
    freq_bins = np.abs(np.fft.fftfreq(len(fft_result), 1 / sample_rate))
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


def _serialize_sliders_for_json(sliders):
    serialized = []
    for slider in sliders or []:
        band = slider.get("range") or [0, 0]
        low, high = sorted([float(band[0]), float(band[1])])
        serialized.append(
            {
                "id": slider.get("id") or f"generic-{uuid.uuid4().hex[:8]}",
                "label": slider.get("label") or "Custom Band",
                "icon": slider.get("icon", "fas fa-sliders-h"),
                "frequency_ranges": [[low, high]],
                "gain": float(slider.get("gain", 1.0)),
            }
        )
    return serialized


def _deserialize_sliders_from_json():
    try:
        with open(_GENERIC_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return [], "Preset file not found."
    except json.JSONDecodeError:
        return [], "Preset file is not valid JSON."

    sliders = data.get("sliders", [])
    result = []
    existing_ids = set()
    for idx, slider in enumerate(sliders):
        freq_ranges = slider.get("frequency_ranges") or slider.get("range") or []
        ranges = []
        if freq_ranges and isinstance(freq_ranges[0], list):
            ranges = [
                [float(pair[0]), float(pair[1])]
                for pair in freq_ranges
                if isinstance(pair, list) and len(pair) >= 2
            ]
        elif isinstance(freq_ranges, list) and len(freq_ranges) >= 2:
            ranges = [[float(freq_ranges[0]), float(freq_ranges[1])]]

        if ranges:
            low, high = ranges[0]
        else:
            low, high = 0.0, 0.0
        slider_id = slider.get("id") or f"generic-{uuid.uuid4().hex[:8]}"
        if slider_id in existing_ids:
            slider_id = f"{slider_id}-{idx}"
        existing_ids.add(slider_id)
        result.append(
            {
                "id": slider_id,
                "label": slider.get("label") or f"Band {idx + 1}",
                "range": [float(low), float(high)],
                "frequency_ranges": ranges or [[float(low), float(high)]],
                "gain": float(slider.get("gain", 1.0)),
                "icon": slider.get("icon", "fas fa-sliders-h"),
            }
        )

    if not result:
        return [], "Preset file contains no sliders."

    return result, f"Loaded {len(result)} slider(s) from JSON."


def register_generic_callbacks(app):
    @app.callback(
        Output("mode-content-area", "children", allow_duplicate=True),
        Output("sliders-container", "children", allow_duplicate=True),
        Input("current-mode", "data"),
        prevent_initial_call=True,
    )
    def _activate_generic_layout(mode):
        if mode != "generic":
            raise PreventUpdate
        return create_generic_controls_area(), _render_empty_state()

    @app.callback(
        Output("generic-range-draft", "data", allow_duplicate=True),
        Output("generic-range-modal", "is_open", allow_duplicate=True),
        Output("generic-range-start", "value", allow_duplicate=True),
        Output("generic-range-end", "value", allow_duplicate=True),
        Output("generic-selection-helper", "children", allow_duplicate=True),
        Output("generic-modal-feedback", "children", allow_duplicate=True),
        Input("frequency-domain", "clickData"),
        Input("generic-clear-selection", "n_clicks"),
        State("generic-range-draft", "data"),
        State("current-mode", "data"),
        State("generic-range-modal", "is_open"),
        prevent_initial_call=True,
    )
    def _capture_band(click_data, clear_clicks, draft, mode, modal_open):
        if mode != "generic":
            raise PreventUpdate

        triggered = ctx.triggered_id

        if triggered == "generic-clear-selection":
            return (
                {"points": []},
                False,
                None,
                None,
                _DEFAULT_HELPER,
                "",
            )

        if triggered != "frequency-domain" or not click_data:
            raise PreventUpdate

        freq = click_data.get("points", [{}])[0].get("x")
        if freq is None:
            raise PreventUpdate

        draft = draft or {"points": []}
        points = list(draft.get("points", []))
        points.append(float(freq))

        if len(points) < 2:
            helper = (
                f"Captured {len(points)}/2 points "
                f"({ _format_freq(freq) } Hz). Select one more."
            )
            return {"points": points}, False, None, None, helper, ""

        low, high = sorted(points[-2:])
        helper = f"Editing band { _format_freq(low) } – { _format_freq(high) } Hz"
        return (
            {"points": []},
            True,
            round(low, 2),
            round(high, 2),
            helper,
            "",
        )

    @app.callback(
        Output("generic-sliders-store", "data", allow_duplicate=True),
        Output("generic-range-modal", "is_open", allow_duplicate=True),
        Output("generic-band-label", "value", allow_duplicate=True),
        Output("generic-modal-feedback", "children", allow_duplicate=True),
        Output("generic-selection-helper", "children", allow_duplicate=True),
        Input("generic-range-confirm", "n_clicks"),
        Input("generic-range-cancel", "n_clicks"),
        State("generic-range-start", "value"),
        State("generic-range-end", "value"),
        State("generic-band-label", "value"),
        State("generic-sliders-store", "data"),
        State("current-mode", "data"),
        prevent_initial_call=True,
    )
    def _finalize_band(confirm, cancel, start, end, label, sliders, mode):
        if mode != "generic":
            raise PreventUpdate

        triggered = ctx.triggered_id
        sliders = sliders or []

        if triggered == "generic-range-cancel":
            return (
                sliders,
                False,
                "",
                "",
                _DEFAULT_HELPER,
            )

        if triggered != "generic-range-confirm":
            raise PreventUpdate

        if start is None or end is None:
            return (
                sliders,
                True,
                label or "",
                "Select two points first.",
                no_update,
            )

        start = float(start)
        end = float(end)
        if start >= end or start < 0 or end < 0:
            return (
                sliders,
                True,
                label or "",
                "Low frequency must be less than high frequency.",
                no_update,
            )

        new_slider = {
            "id": f"generic-{uuid.uuid4().hex[:8]}",
            "label": (label or "").strip() or f"Band {len(sliders) + 1}",
            "range": [round(start, 2), round(end, 2)],
            "frequency_ranges": [[round(start, 2), round(end, 2)]],
            "gain": 1.0,
        }
        return (
            sliders + [new_slider],
            False,
            "",
            "",
            _DEFAULT_HELPER,
        )

    @app.callback(
        Output("generic-sliders-store", "data", allow_duplicate=True),
        Input({"type": "generic-delete-slider", "index": ALL}, "n_clicks"),
        State("generic-sliders-store", "data"),
        prevent_initial_call=True,
    )
    def _delete_slider(n_clicks, sliders):
        if not ctx.triggered_id or not sliders:
            raise PreventUpdate
        slider_id = ctx.triggered_id.get("index")
        if slider_id is None:
            raise PreventUpdate
        triggered_value = ctx.triggered[0].get("value") if ctx.triggered else None
        if not triggered_value:
            raise PreventUpdate
        new_sliders = [s for s in sliders if s["id"] != slider_id]
        if len(new_sliders) == len(sliders):
            raise PreventUpdate
        return new_sliders

    @app.callback(
        Output("sliders-container", "children", allow_duplicate=True),
        Input("generic-sliders-store", "data"),
        State("current-mode", "data"),
        prevent_initial_call=True,
    )
    def _render_slider_row(sliders, mode):
        if mode != "generic":
            raise PreventUpdate
        if not sliders:
            return _render_empty_state()
        return [_build_slider_card(slider) for slider in sliders]

    @app.callback(
        Output("generic-sliders-store", "data", allow_duplicate=True),
        Input({"type": "generic-slider", "index": ALL}, "value"),
        State({"type": "generic-slider", "index": ALL}, "id"),
        State("generic-sliders-store", "data"),
        State("current-mode", "data"),
        prevent_initial_call=True,
    )
    def _sync_slider_values(values, ids, sliders, mode):
        if mode != "generic" or not sliders or not values:
            raise PreventUpdate
        slider_map = {
            comp_id["index"]: val for comp_id, val in zip(ids, values) if val is not None
        }
        updated = False
        new_data = []
        for slider in sliders:
            slider_id = slider["id"]
            new_gain = slider_map.get(slider_id, slider.get("gain", 1.0))
            if not np.isclose(new_gain, slider.get("gain", 1.0)):
                updated = True
                new_slider = dict(slider, gain=float(new_gain))
            else:
                new_slider = slider
            new_data.append(new_slider)

        if not updated:
            raise PreventUpdate
        return new_data

    @app.callback(
        Output("generic-json-feedback", "children", allow_duplicate=True),
        Input("generic-save-json", "n_clicks"),
        State("generic-sliders-store", "data"),
        State("current-mode", "data"),
        prevent_initial_call=True,
    )
    def _save_generic_presets(save_clicks, sliders, mode):
        if mode != "generic" or not save_clicks:
            raise PreventUpdate

        serialized = _serialize_sliders_for_json(sliders)
        payload = {"name": "Generic", "sliders": serialized}

        try:
            os.makedirs(os.path.dirname(_GENERIC_JSON_PATH), exist_ok=True)
            with open(_GENERIC_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except OSError as exc:
            return f"Failed to save presets: {exc}"

        return f"Saved {len(serialized)} slider(s) to JSON."

    @app.callback(
        Output("generic-sliders-store", "data", allow_duplicate=True),
        Output("generic-json-feedback", "children", allow_duplicate=True),
        Input("generic-load-json", "n_clicks"),
        State("current-mode", "data"),
        prevent_initial_call=True,
    )
    def _load_generic_presets(load_clicks, mode):
        if mode != "generic" or not load_clicks:
            raise PreventUpdate

        sliders, message = _deserialize_sliders_from_json()
        if not sliders:
            return no_update, message
        return sliders, message

    @app.callback(
        Output("processed-signal-store", "data", allow_duplicate=True),
        Output("spectrogram-post", "figure", allow_duplicate=True),
        Output("frequency-domain", "figure", allow_duplicate=True),
        Output("frequency-domain-data", "data", allow_duplicate=True),
        Input("generic-sliders-store", "data"),
        State("signal-data-store", "data"),
        State("current-mode", "data"),
        State("scale-audiogram", "active"),
        prevent_initial_call=True,
    )
    def _process_generic_signal(sliders, signal_data, mode, audiogram_active):
        if mode != "generic" or not signal_data:
            raise PreventUpdate

        fft_module = _get_fft_module()
        cache_entry = _get_cached_fft(signal_data, fft_module)
        original_signal = cache_entry["original_signal"]
        base_fft = cache_entry["base_fft"]
        freq_bins = cache_entry["freq_bins"]
        original_spec_fig = cache_entry.get("original_spec_fig")
        original_freq_fig = cache_entry.get("original_freq_fig")
        sample_rate = signal_data["sample_rate"]

        sliders = sliders or []
        active_sliders = [
            slider for slider in sliders if not np.isclose(slider.get("gain", 1.0), 1.0)
        ]

        scale_mode = "audiogram" if audiogram_active else "linear"

        if base_fft.size == 0 or not active_sliders:
            processed = original_signal
            modified_fft = base_fft
        else:
            modified_fft = _apply_bands(base_fft, freq_bins, active_sliders)
            processed_complex = fft_module.ifft(modified_fft.tolist())
            processed = np.array([x.real for x in processed_complex])[: len(original_signal)]

        if processed.size:
            max_val = np.max(np.abs(processed))
            if max_val > 1.0:
                processed = processed * (0.99 / max_val)

        processed_list = processed.astype(float).tolist()
        processed_data = {
            "samples": processed_list,
            "signal": processed_list,
            "sample_rate": sample_rate,
        }

        if active_sliders:
            f, t, Sxx = _spectrogram_subset(processed, sample_rate, fft_module)
            spec_fig = create_spec_figure(f, t, Sxx)
            freqs, mags = _fft_to_freq_arrays(modified_fft, sample_rate)
            freq_payload = {"frequencies": freqs, "magnitudes": mags}
            freq_fig = create_freq_figure(freqs, mags, use_db=True, scale_mode=scale_mode) if freqs else no_update
        else:
            spec_fig = copy.deepcopy(original_spec_fig) if original_spec_fig else create_spec_figure(*_spectrogram_subset(original_signal, sample_rate, fft_module))
            freqs, mags = _fft_to_freq_arrays(base_fft, sample_rate)
            freq_payload = {"frequencies": freqs, "magnitudes": mags}
            if original_freq_fig and scale_mode == "linear":
                freq_fig = copy.deepcopy(original_freq_fig)
            else:
                freq_fig = create_freq_figure(freqs, mags, use_db=True, scale_mode=scale_mode) if freqs else no_update

        return processed_data, spec_fig, freq_fig, freq_payload

    @app.callback(
        Output("audio-player-before", "src", allow_duplicate=True),
        Input("signal-data-store", "data"),
        State("current-mode", "data"),
        prevent_initial_call=True,
    )
    def _sync_original_audio(signal_data, mode):
        if mode != "generic" or not signal_data:
            raise PreventUpdate

        signal = np.array(signal_data.get("samples") or signal_data.get("signal"))
        sample_rate = signal_data["sample_rate"]
        return audio_to_base64_uri(signal, sample_rate, normalize=False)

    @app.callback(
        Output("audio-player-after", "src", allow_duplicate=True),
        Input("processed-signal-store", "data"),
        State("current-mode", "data"),
        prevent_initial_call=True,
    )
    def _sync_processed_audio(processed_data, mode):
        if mode != "generic" or not processed_data:
            raise PreventUpdate

        signal = np.array(processed_data.get("samples") or processed_data.get("signal"))
        sample_rate = processed_data["sample_rate"]
        return audio_to_base64_uri(signal, sample_rate, normalize=False)