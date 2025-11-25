"""Utilities for converting FFT data to audiogram-style axes."""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple, Optional

import numpy as np

# Standard octave frequencies used in clinical audiograms.
_OCTAVE_FREQUENCIES = np.array(
    [125, 250, 500, 1000, 2000, 4000, 8000, 16000], dtype=float
)


def _format_tick(freq_hz: float) -> str:
    """Return a short label for axis tick values."""
    if freq_hz >= 1000:
        value = freq_hz / 1000
        return f"{value:g}k"
    return f"{int(freq_hz)}"


def _db_to_hl(db_values: np.ndarray) -> np.ndarray:
    """
    Convert magnitude in dB into Audiogram dB HL.
    
    Maps the dB values to the 0-120 HL range where:
    - 0 dB HL = normal hearing threshold (top of graph)
    - 120 dB HL = profound hearing loss (bottom of graph)
    
    The mapping is: HL = 120 - (dB + 120) = -dB
    Clamped to [0, 120] range.
    """
    if db_values.size == 0:
        return db_values

    # Normalize dB values to 0-120 range
    # Map from dB range to HL range
    db_values = np.asarray(db_values, dtype=float)
    
    # Simple linear mapping: treat input dB as hearing level
    # Lower dB = better hearing (lower HL number)
    # Higher dB = worse hearing (higher HL number)
    hl = -db_values + 60  # Offset to put typical values in 0-120 range
    
    return np.clip(hl, 0, 120)


def to_audiogram_axes(
    frequencies: Sequence[float], magnitudes_db: Sequence[float]
) -> Tuple[List[float], List[float], Dict[str, Dict], Optional[List[str]]]:
    """
    Convert dense FFT data into octave-discrete points with Audiogram dB HL.

    Returns:
        scaled_freqs: Octave-band center frequencies (Hz)
        scaled_levels: Audiogram HL magnitudes aligned to the octave grid
        axis_overrides: Layout fragments for Plotly axes
        hover_labels: Text labels to show real frequencies in tooltips
    """
    if frequencies is None or magnitudes_db is None:
        return [], [], {}, []

    freq_arr = np.asarray(frequencies, dtype=float)
    mag_arr = np.asarray(magnitudes_db, dtype=float)

    if freq_arr.size == 0 or mag_arr.size == 0:
        return [], [], {}, []

    valid = np.isfinite(freq_arr) & np.isfinite(mag_arr)
    if not np.any(valid):
        return [], [], {}, []

    freq_arr = freq_arr[valid]
    mag_arr = mag_arr[valid]

    order = np.argsort(freq_arr)
    freq_arr = freq_arr[order]
    mag_arr = mag_arr[order]

    # Filter octave frequencies to only those within data range
    max_freq = freq_arr.max()
    valid_octaves = _OCTAVE_FREQUENCIES[_OCTAVE_FREQUENCIES <= max_freq]
    
    print(f"[AUDIOGRAM] freq_arr range: {freq_arr.min():.2f} - {freq_arr.max():.2f}")
    print(f"[AUDIOGRAM] All octaves: {_OCTAVE_FREQUENCIES}")
    print(f"[AUDIOGRAM] Valid octaves (within data range): {valid_octaves}")
    
    if len(valid_octaves) == 0:
        print("[AUDIOGRAM] No valid octaves found!")
        return [], [], {}, []

    interp_levels = np.interp(
        valid_octaves,
        freq_arr,
        mag_arr,
        left=mag_arr[0],
        right=mag_arr[-1],
    )
    
    print(f"[AUDIOGRAM] Before _db_to_hl: {interp_levels}")
    
    hl_levels = _db_to_hl(interp_levels)
    
    print(f"[AUDIOGRAM] After _db_to_hl: {hl_levels}")

    category_labels = [_format_tick(freq) for freq in valid_octaves]
    hover_labels = [
        f"{int(freq)} Hz" if freq < 1000 else f"{freq/1000:g} kHz"
        for freq in valid_octaves
    ]

    axis_overrides = {
        "xaxis": {
            "title": "Frequency (Hz)",
            "type": "log",
            "tickvals": valid_octaves.tolist(),
            "ticktext": category_labels,
            "range": [
                float(np.log10(valid_octaves[0])),
                float(np.log10(valid_octaves[-1])),
            ],
        },
        "yaxis": {
            "title": "Audiogram dB HL",
            "range": [120, 0],
        },
    }

    return (
        valid_octaves.tolist(),
        hl_levels.tolist(),
        axis_overrides,
        hover_labels,
    )