import numpy as np
from scipy.io import wavfile
import soundfile as sf
from pathlib import Path

def load_audio(file_path):
    """
    Load any audio file and return the signal and sample rate.
    
    Parameters:
    -----------
    file_path : str or Path
        Path to the audio file (supports mp3, wav, flac, ogg, m4a, etc.)
    
    Returns:
    --------
    signal : numpy.ndarray
        Audio signal as a numpy array
        Shape: (n_samples,)
    sample_rate : int
        Sample rate of the audio file in Hz
    
    Examples:
    ---------
    >>> signal, sr = load_audio('song.mp3')
    
    >>> signal, sr = load_audio('audio.wav')
    """
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    try:
        # Use soundfile for universal audio loading
        # It handles mp3, wav, flac, ogg, and many other formats
        signal, sample_rate = sf.read(str(file_path), dtype='float32')
        
        return signal, sample_rate
        
    except Exception as e:
        raise RuntimeError(f"Error loading audio file: {e}")

def save_audio_as_wav(signal, sample_rate, output_path, bit_depth=16, normalize=False):
    """
    Save audio signal as a WAV file.
    
    Parameters:
    -----------
    signal : numpy.ndarray
        Audio signal array
        Shape: (n_samples,) for mono or (n_samples, n_channels) for stereo
    sample_rate : int
        Sample rate in Hz (e.g., 44100, 48000, 16000)
    output_path : str or Path
        Output file path (will add .wav extension if not present)
    bit_depth : int, default=16
        Bit depth for output file (8, 16, 24, or 32)
        16-bit is standard CD quality
    normalize : bool, default=False
        If True, normalize audio to maximum amplitude without clipping
    
    Returns:
    --------
    output_path : Path
        Path to the saved WAV file
    
    Examples:
    ---------
    >>> signal, sr = load_audio('song.mp3')
    >>> save_audio_as_wav(signal, sr, 'output.wav')
    
    >>> # Save with normalization and 24-bit depth
    >>> save_audio_as_wav(signal, sr, 'output.wav', bit_depth=24, normalize=True)
    """
    output_path = Path(output_path)
    
    # Add .wav extension if not present
    if output_path.suffix.lower() != '.wav':
        output_path = output_path.with_suffix('.wav')
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Make a copy to avoid modifying original
    audio_data = np.array(signal, copy=True)
    
    # Normalize if requested
    if normalize:
        max_val = np.abs(audio_data).max()
        if max_val > 0:
            audio_data = audio_data / max_val * 0.99  # Leave small headroom
    
    # Map bit depth to soundfile subtype
    subtype_map = {
        8: 'PCM_U8',   # 8-bit unsigned
        16: 'PCM_16',  # 16-bit signed (standard)
        24: 'PCM_24',  # 24-bit signed
        32: 'PCM_32',  # 32-bit signed
    }
    
    if bit_depth not in subtype_map:
        raise ValueError(f"Bit depth must be one of {list(subtype_map.keys())}, got {bit_depth}")
    
    subtype = subtype_map[bit_depth]
    
    try:
        # Save using soundfile
        sf.write(str(output_path), audio_data, sample_rate, subtype=subtype)
        print(f"Audio saved to: {output_path}")
        print(f"Sample rate: {sample_rate} Hz")
        print(f"Bit depth: {bit_depth}-bit")
        print(f"Duration: {len(audio_data)/sample_rate:.2f} seconds")
        
        return output_path
        
    except Exception as e:
        raise RuntimeError(f"Error saving WAV file: {e}")