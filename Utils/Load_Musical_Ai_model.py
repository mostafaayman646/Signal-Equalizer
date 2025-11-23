import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

if current not in sys.path:
    sys.path.insert(0, current)


from openunmix import predict
import stempeg
import torch
import torchaudio
from IPython.display import Audio, display
import numpy as np
from Utils.load_save_audio import load_audio

use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")

def Audio_Seprator(signal_data, sr=None):
    # Extract signal and sample rate from the dictionary
    signal = np.array(signal_data['samples'])  # or signal_data['signal']
    sr = signal_data['sample_rate'] if sr is None else sr
    
    # Ensure audio is 2D: (channels, samples)
    audio = signal.copy()

    if audio.ndim == 1:
        # mono → reshape to (1, samples)
        audio = audio[np.newaxis, :]
    else:
        # stereo shape (samples, channels) → transpose
        audio = audio.T

    # Convert to torch tensor
    audio_tensor = torch.as_tensor(audio).float()

    # Run Open-Unmix separation
    estimates = predict.separate(
        audio=audio_tensor,
        rate=sr,
        device=device,
        niter=10
    )
    
    results = {}
    for target, estimate in estimates.items():
        print(target)
        estimate_np = estimate.detach().cpu().numpy()
        results[target] = estimate_np[0].tolist()  # Store for return if needed
    
    return results