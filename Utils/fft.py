# How to use fft (linear and audiogram scale) and ifft
# To use the linear fft function simply call time_to_frequency_linear and pass the signal as a list with its sampling rate.
# To use the audiogram fft function ,call time_to_frequency_audiogram and pass the signal as a list with its sampling rate.
# to use ifft call frequency_to_time function and pass the signal as a list with its sampling rate.
# the result should be dictionaries with magnitudes, frequencies that can be plotted

from math import ceil, sqrt, tau, log10
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

# Helper function for ifft
def ifft(X: List[complex]) -> List[complex]:
    """Compute the inverse FFT using conjugate trick."""
    N = len(X)
    conjX = [x.conjugate() for x in X]
    y = fft(conjX)
    return [x.conjugate() / N for x in y]

# Main functions that controls the flow
def time_to_frequency_linear(signal: List[float], sampling_rate: float):
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


def frequency_to_time(fft_result: List[complex]) -> List[float]:

    time_domain = ifft(fft_result)
    return [x.real for x in time_domain]


def time_to_frequency_audiogram(signal: List[float], sampling_rate: float):

    # Get regular linear FFT
    fft_data = time_to_frequency_linear(signal, sampling_rate)
    
    frequencies = fft_data['frequencies']
    magnitude = fft_data['magnitude']
    
    # Convert magnitude to dB scale (common for audiograms)
    magnitude_db = []
    for mag in magnitude:
        if mag > 1e-10:
            db = 20 * log10(mag)
        else:
            db = -120  # Floor value
        magnitude_db.append(db)
    
    return {
        'frequencies': frequencies,      # Same frequencies, but plot with log scale
        'magnitude': magnitude,          # Linear magnitude
        'magnitude_db': magnitude_db,    # dB magnitude (typical for audiograms)
        'full_fft': fft_data['full_fft']
    }