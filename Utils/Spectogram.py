import numpy as np
from fft import *

def simple_spectrogram(X, fs, fft_size, hop_size):
    """
    Computes a simple spectrogram based on the core STFT logic.
    
    Args:
        X (np.array): The input signal (1D array).
        fs (int): The sampling rate (in Hz).
        fft_size (int): The size of the FFT (this will also be the window size).
        hop_size (int): The number of samples to hop between frames.
        
    Returns:
        f (np.array): Array of frequency bins (y-axis).
        t (np.array): Array of time bins (x-axis).
        Sxx (np.array): The 2D spectrogram matrix (amplitude is power).
    """
    
    # 1. Get the total length of the signal
    signal_len = len(X)
    
    # 2. Create a window
    # The Hanning window "fades" the edges of your signal chunk down to zero before you pass it to the FFT.
    window = np.hanning(fft_size)
    
    # 3. Create an empty list to store the FFT results for each frame
    # (These will be the columns of our spectrogram)
    spectrogram_cols = []
    
    # 4. Calculate fft for all signal
    
    fft_result = process_signal(X.tolist(),fs)
    
    # 4. Loop through the signal in overlapping-windowed "hops"
    # We start at index 0
    current_index = 0
    while current_index + fft_size <= signal_len:
        # --- Step A: Get the frame (a "slice" of the signal) ---
        frame = X[current_index : current_index + fft_size]
        
        # --- Step B: Apply the window to the frame ---
        windowed_frame = frame * window
        
        # --- Step C: Compute the FFT ---
        fft_data = process_signal(windowed_frame.tolist(), fs)
        
        # --- Step D: Get the power (magnitude squared) ---
        # The FFT result is complex. We just want its magnitude (amplitude).
        # We square it to get the "power" (Power Spectral Density).
        power_spectrum = np.array(fft_data['magnitude'])**2
        
        # --- Step E: Add the result to our list of columns ---
        spectrogram_cols.append(power_spectrum)
        
        # --- Step F: "Hop" to the next frame's starting position ---
        current_index += hop_size
        
    # 5. Combine all frame results into a 2D matrix
    # We stack our list of columns and transpose (.T) it
    # so that frequency is on the y-axis and time is on the x-axis.
    Sxx = np.array(spectrogram_cols).T
    
    # 6. Calculate the frequency axis (y-axis)
    # This is a standard numpy function that gives the frequencies for an rfft.
    f = fft_result['frequencies']
    
    # 7. Calculate the time axis (x-axis)
    # This is the start time of each frame (column) in our spectrogram.
    num_frames = Sxx.shape[1]
    t = np.arange(num_frames) * hop_size / fs
    
    return f, t, Sxx