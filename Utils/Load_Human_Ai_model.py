import os
import sys
import numpy as np
import torch
import torchaudio
import soundfile as sf
from asteroid.models import BaseModel

# Import the class from the new file we just created
from Utils.multi_decoder_dprnn import MultiDecoderDPRNN


# --- WINDOWS PATCHES (CRITICAL) ---
# 1. Fix 'libtorchcodec' crash by forcing soundfile
def safe_save_wrapper(filepath, src, sample_rate, **kwargs):
    if hasattr(src, 'detach'):
        src = src.detach().cpu().numpy()
    # Handle dimensions: (Channels, Time) -> (Time, Channels) for soundfile
    if src.ndim == 2 and src.shape[0] < src.shape[1]:
        src = src.T
    sf.write(str(filepath), src, sample_rate)


# 2. Patch load to avoid FFmpeg issues
def safe_load_wrapper(filepath, *args, **kwargs):
    audio_data, sample_rate = sf.read(filepath)
    waveform = torch.from_numpy(audio_data).float()
    if waveform.dim() == 1:
        waveform = waveform.unsqueeze(0)
    else:
        waveform = waveform.T  # Ensure (Channels, Time)
    return waveform, sample_rate


# Apply Patches
torchaudio.save = safe_save_wrapper
torchaudio.load = safe_load_wrapper


# ----------------------------------

def Separate_Voices(file_path):
    """
    Runs the custom Multi-Decoder DPRNN model using the logic from 'separate.py'.
    """
    if not file_path or not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    print(f"🗣️ Starting Custom AI Separation on: {file_path}")

    # --- PATCH 3: Security Bypass for PyTorch 2.6 ---
    original_load = torch.load

    def unsafe_load_wrapper(*args, **kwargs):
        kwargs['weights_only'] = False
        return original_load(*args, **kwargs)

    # ------------------------------------------------

    try:
        # Apply Security Patch
        torch.load = unsafe_load_wrapper

        # 1. Load the Model using the CUSTOM class
        print("Loading MultiDecoderDPRNN...")
        model = MultiDecoderDPRNN.from_pretrained("JunzheJosephZhu/MultiDecoderDPRNN").eval()

        # Restore Security
        torch.load = original_load

        if torch.cuda.is_available():
            model.cuda()

        # 2. Load Audio (Using patched safe loader)
        mixture, sample_rate = torchaudio.load(file_path)
        if torch.cuda.is_available():
            mixture = mixture.cuda()

        # 3. Run Inference
        print("Running inference...")
        # The model's .separate() method handles the logic
        sources_est = model.separate(mixture)

        # Move to CPU for saving
        sources_est = sources_est.cpu()

        # 4. Save Results
        filename_no_ext = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = os.path.join(os.getcwd(), "static", "separated", "voices", filename_no_ext)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        stems = {}

        # Iterate over separated sources
        # The model outputs (Sources, Time) or (Batch, Sources, Time)
        # model.separate usually removes batch dim if input was 1D/2D

        num_speakers = sources_est.shape[0]
        print(f"Model detected {num_speakers} speakers.")

        for i, source in enumerate(sources_est):
            stem_name = f"Speaker_{i + 1}"
            save_path = os.path.join(output_dir, f"{stem_name}.wav")

            # Use the patched save (which uses soundfile)
            # source[None] adds a channel dim -> (1, Time)
            torchaudio.save(save_path, source[None], sample_rate)

            stems[stem_name] = save_path

        return stems

    except Exception as e:
        torch.load = original_load
        print(f"Model Error: {e}")
        import traceback
        traceback.print_exc()
        return None


# Reuse Mixing Function (Standard for both apps)
def Mix_Human_Audio(stems_paths, gains, output_filename="human_mixed_output.wav"):
    mixed_signal = None
    sample_rate = 8000

    for name, path in stems_paths.items():
        if not os.path.exists(path): continue
        gain = gains.get(name, 1.0)
        try:
            data, sr = sf.read(path)
            sample_rate = sr
            if len(data.shape) > 1: data = data.mean(axis=1)
            data = data * gain
            if mixed_signal is None:
                mixed_signal = data
            else:
                if len(data) > len(mixed_signal):
                    mixed_signal = np.pad(mixed_signal, (0, len(data) - len(mixed_signal)))
                    mixed_signal += data
                else:
                    data = np.pad(data, (0, len(mixed_signal) - len(data)))
                    mixed_signal += data
        except:
            continue

    if mixed_signal is None: return None
    max_val = np.max(np.abs(mixed_signal))
    if max_val > 1.0: mixed_signal = mixed_signal / max_val

    static_dir = os.path.join(os.getcwd(), "static")
    if not os.path.exists(static_dir): os.makedirs(static_dir)
    output_path = os.path.join(static_dir, output_filename)
    sf.write(output_path, mixed_signal, sample_rate)
    return output_filename