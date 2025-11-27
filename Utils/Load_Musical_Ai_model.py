import os
import sys
import numpy as np
from scipy.io import wavfile
import torchaudio
import soundfile as sf  # Ensure pip install soundfile
from demucs import separate



def safe_save_wrapper(filepath, src, sample_rate, **kwargs):

    # 1. Convert PyTorch Tensor to Numpy
    if hasattr(src, 'detach'):
        src = src.detach().cpu().numpy()

    # 2. Transpose dimensions:
    # Torchaudio uses (Channels, Time), Soundfile expects (Time, Channels)
    if src.ndim == 2 and src.shape[0] < src.shape[1]:
        src = src.T

    # 3. Save using soundfile (ignoring complex encoding arguments from Demucs)
    sf.write(str(filepath), src, sample_rate)


# APPLY THE PATCH
torchaudio.save = safe_save_wrapper


# -------------------------

def Audio_Seprator(file_path, model="htdemucs"):
    """
    Runs Demucs directly as a library function.
    Saves output to 'static/separated' to avoid Dash hot-reload loops.
    """
    if not file_path or not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    # print(f"🎵 Starting AI Separation on: {file_path}")

    try:
        # Prepare arguments exactly like the command line
        # We use the -n (model) and the file path
        # -o specifies output directory. We point it to 'static/separated'
        output_root = os.path.join(os.getcwd(), "static", "separated")
        args = ["-n", model, "-o", output_root, file_path]

        # Run Demucs Main Function directly
        separate.main(args)

    except SystemExit as e:
        if e.code != 0:
            print(f"Demucs stopped with exit code: {e.code}")
            return None
    except Exception as e:
        print(f"Demucs Internal Error: {e}")
        import traceback
        traceback.print_exc()
        return None

    # 2. Locate the Output Files
    # Demucs saves to: static/separated/htdemucs/{filename_without_extension}/
    filename_no_ext = os.path.splitext(os.path.basename(file_path))[0]

    output_base = os.path.join(os.getcwd(), "static", "separated", model, filename_no_ext)

    # Fallback search if filename cleaning happened
    if not os.path.exists(output_base):
        search_base = os.path.join(os.getcwd(), "static", "separated", model)
        if os.path.exists(search_base):
            potential_folders = os.listdir(search_base)
            # Find newest folder
            potential_folders.sort(key=lambda x: os.path.getmtime(os.path.join(search_base, x)), reverse=True)
            if potential_folders:
                output_base = os.path.join(search_base, potential_folders[0])

    if not os.path.exists(output_base):
        print(f"❌ Could not find output folder: {output_base}")
        return None

    # 3. Create a Dictionary of Stems
    stems = {}
    for f in os.listdir(output_base):
        if f.endswith(".wav"):
            stem_name = f.replace(".wav", "")
            stems[stem_name] = os.path.join(output_base, f)

    print(f"✅ Separation Complete. Stems found: {list(stems.keys())}")
    return stems


def Mix_Audio(stems_paths, gains, output_filename="ai_mixed_output.wav"):
    """
    Mixes the stem files together based on the gain values.
    Saves the result to the 'static' folder (NOT assets).
    """
    mixed_signal = None
    sample_rate = 44100

    for name, path in stems_paths.items():
        if not os.path.exists(path):
            continue

        gain = gains.get(name, 1.0)

        try:
            sr, data = wavfile.read(path)
            sample_rate = sr

            if data.dtype != np.float32:
                data = data.astype(np.float32)

            data = data * gain

            if mixed_signal is None:
                mixed_signal = data
            else:
                min_len = min(len(data), len(mixed_signal))
                mixed_signal = mixed_signal[:min_len] + data[:min_len]

        except Exception as e:
            print(f"Error reading stem {path}: {e}")
            continue

    if mixed_signal is None:
        return None

    # Clip and Convert
    max_val = np.max(np.abs(mixed_signal))
    if max_val > 32767:
        mixed_signal = mixed_signal * (32767 / max_val)

    mixed_signal = mixed_signal.astype(np.int16)

    # SAVE TO STATIC (Crucial Change)
    static_dir = os.path.join(os.getcwd(), "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    output_path = os.path.join(static_dir, output_filename)
    wavfile.write(output_path, sample_rate, mixed_signal)

    return output_filename