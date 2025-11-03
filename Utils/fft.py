"""
FFT Utility - Quick Start:
Import:
    from fft import process_signal
Usage:
    result = process_signal(signal_array, sampling_rate)
Returns dict with keys:
    'frequencies' - frequency bins (Hz)
    'magnitude' - amplitude spectrum for plotting
    'full_fft' - complex FFT data for further processing
Example:
    result = process_signal(audio_data, 44100)
    freq_axis = result['frequencies']
    magnitude = result['magnitude']
"""

from math import ceil, sqrt, tau
from functools import cache
from typing import List, Union
import cmath

# Helper Functions for FFT
def get_factor(p: int) -> Union[int, None]:
    """Return the lowest factor of p (or None if prime)."""
    if not p & 1:
        return 2
    for d in range(3, ceil(sqrt(p)) + 1, 2):
        if p % d == 0:
            return d
    return None

def get_twiddle(n: int, x: int) -> complex:
    """Compute the twiddle factor: exp(-j * 2pi * (x/n))"""
    x = x % n
    angle = x * tau / n
    return cmath.exp(-1j * angle)

# FFT Implementation
def fft(A: List[complex]) -> List[complex]:
    """
    Recursive FFT implementation.
    A should be a list of complex numbers whose length is ideally a power of 2
    or decomposable by factors.
    """
    N = len(A)
    r2 = get_factor(N)
    if r2 is None or N == 1:
        return [sum(A[k] * get_twiddle(N, j * k) for k in range(N)) for j in range(N)]

    r1 = N // r2
    A1 = []
    for k0 in range(r2):
        subseq = A[k0:N:r2]
        A1.append(fft(subseq))

    X = [0] * N
    for j1 in range(r2):
        for j0 in range(r1):
            X[j1 * r1 + j0] = sum(
                A1[k0][j0] * get_twiddle(r2, j1 * k0) * get_twiddle(N, j0 * k0)
                for k0 in range(r2)
            )
    return X

# Inverse FFT (may be needed later, not tested yet)

def ifft(X: List[complex]) -> List[complex]:
    """Compute the inverse FFT using conjugate trick."""
    N = len(X)
    conjX = [x.conjugate() for x in X]
    y = fft(conjX)
    return [x.conjugate() / N for x in y]

# Main function that controls the flow
def process_signal(signal: List[float], sampling_rate: float):
    """
    Takes a time-domain signal and a sampling rate, computes the FFT,
    and returns a dictionary with:
      - frequencies: frequency bins (x-axis) in Hz (linear scale)
      - magnitude: magnitude spectrum (amplitude for plotting)
      - full_fft: the complete FFT output (for later reconstruction)
    """
    # Convert the real signal to a list of complex numbers
    signal_complex = [complex(x, 0) for x in signal]

    # Compute the full FFT
    fft_result = fft(signal_complex)
    N = len(fft_result)

    # Create frequency axis (only for non-negative frequencies since signal is real)
    num_bins = N // 2 + 1
    frequencies = [k * sampling_rate / N for k in range(num_bins)]

    # Compute magnitude for each frequency bin (for plotting)
    magnitude = [abs(fft_result[k]) for k in range(num_bins)]

    return {
        'frequencies': frequencies,  # x-axis: Frequency bins (Hz)
        'magnitude': magnitude,      # y-axis: Amplitude spectrum for plotting
        'full_fft': fft_result       # Full FFT for equalization and reconstruction
    }