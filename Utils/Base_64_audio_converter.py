import base64
import io
import soundfile as sf
import numpy as np

def audio_to_base64_uri(signal, sample_rate, bit_depth=16, normalize=False):
    """
    Convert audio signal to base64 data URI.
    
    Parameters:
    -----------
    signal : numpy.ndarray
        Audio signal array
        Shape: (n_samples,) for mono or (n_samples, n_channels) for stereo
    sample_rate : int
        Sample rate in Hz (e.g., 44100, 48000, 16000)
    bit_depth : int, default=16
        Bit depth for output (8, 16, 24, or 32)
        16-bit is standard CD quality
    normalize : bool, default=False
        If True, normalize audio to maximum amplitude without clipping
    
    Returns:
    --------
    str
        Base64 data URI string (data:audio/wav;base64,...)
        Can be used directly in HTML audio tags or JavaScript
    
    Examples:
    ---------
    >>> data_uri = audio_to_base64_uri(signal, sr)
    >>> print(data_uri[:50])  # First 50 chars
    data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAA...
    """
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
        # Write audio to in-memory bytes buffer
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, subtype=subtype, format='WAV')
        
        # Get bytes and encode to base64
        buffer.seek(0)
        audio_bytes = buffer.read()
        base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Create data URI
        data_uri = f"data:audio/wav;base64,{base64_audio}"
        
        return data_uri
        
    except Exception as e:
        raise RuntimeError(f"Error converting audio to base64: {e}")