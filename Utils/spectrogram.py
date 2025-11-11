import numpy as np

def spectrogram(X, fs, fft_module, fft_size = 1024, hop_size = 512):
    """
    Computes a simple spectrogram based on the core STFT logic,
    using the provided C++ fft_module.
    
    Args:
        X (np.array): The input signal (1D array).
        fs (int): The sampling rate (in Hz).
        fft_module (module): The imported C++ FFT module.
        fft_size (int): The size of the FFT (this will also be the window size).
        hop_size (int): The number of samples to hop between frames.
        
    Returns:
        f (np.array): Array of frequency bins (y-axis).
        t (np.array): Array of time bins (x-axis).
        Sxx (np.array): The 2D spectrogram matrix (amplitude is power).
    
    Examples:
    ---------
    >>> # Note: Now requires fft_module
    >>> # f, t, Sxx = spectrogram(signal, sample_rate, fft_module)
    """
    
    # 1. Get the total length of the signal
    signal_len = len(X)
    
    # 2. Create a window
    window = np.hanning(fft_size)
    
    # 3. Create an empty list to store the FFT results for each frame
    spectrogram_cols = []
    
    # 4. Loop through the signal in overlapping-windowed "hops"
    current_index = 0
    while current_index + fft_size <= signal_len:
        # --- Step A: Get the frame ---
        frame = X[current_index : current_index + fft_size]
        
        # --- Step B: Apply the window to the frame ---
        windowed_frame = frame * window
        
        # --- Step C: Compute the FFT ---
        frame_complex = windowed_frame.astype(complex) 
        
        # +++ ADDED: Call the fast C++ module
        fft_result_complex = fft_module.fft(frame_complex)
        
        # --- Step D: Get the power (magnitude squared) ---
        # We only need the first half (positive frequencies) + DC
        N_fft = len(fft_result_complex) # This will be fft_size
        num_bins = N_fft // 2 + 1
        
        # Get magnitudes and square for power
        fft_magnitudes = np.abs(fft_result_complex[:num_bins])
        power_spectrum = fft_magnitudes**2
        
        # --- Step E: Add the result to our list of columns ---
        spectrogram_cols.append(power_spectrum)
        
        # --- Step F: "Hop" to the next frame's starting position ---
        current_index += hop_size
        
    # 5. Combine all frame results into a 2D matrix
    Sxx = np.array(spectrogram_cols).T
    
    # 6. Calculate the frequency axis (y-axis)
    N_bins = fft_size // 2 + 1
    f = np.arange(N_bins) * fs / fft_size
    
    # 7. Calculate the time axis (x-axis)
    num_frames = Sxx.shape[1]
    t = np.arange(num_frames) * hop_size / fs
    
    return f, t, Sxx