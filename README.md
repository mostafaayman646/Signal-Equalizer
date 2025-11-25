# Signal Equalizer Pro

A professional audio signal processing application that provides frequency domain equalization with real-time visualization and AI-powered audio processing capabilities.

## Overview

Signal Equalizer Pro is a web-based audio processing tool built with Dash and Plotly that allows users to:
- Upload and analyze audio signals in the frequency and time-frequency domains
- Apply customized equalization using interactive frequency sliders
- Leverage AI models for source separation (human voices, musical instruments, and animal sounds)
- Visualize audio characteristics using multiple graph types
- Download processed audio files

The application supports both generic and AI-powered equalization modes, providing flexibility for various audio processing tasks.

## Folder Structure

```
Signal-Equalizer/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── components/                      # UI components and layouts
│   ├── layout_builder.py           # Main layout construction
│   ├── tab_callbacks.py            # Tab event handlers
│   ├── callbacks/                  # Feature-specific callbacks
│   │   ├── Upload_signal.py
│   │   ├── PlayAudio.py
│   │   ├── Download_Audio.py
│   │   ├── NavBar_Mode_Switch.py
│   │   ├── Toggle_spectogram.py
│   │   └── Scale_toggle.py
│   └── layouts/                    # Graph and UI layout definitions
│       ├── freq_fig.py            # Frequency domain visualization
│       ├── spec_figure_layout.py  # Spectrogram visualization
│       └── Create_Sliders_Area.py # Equalizer slider interface
│
├── modes/                           # Processing modes
│   ├── generic/                    # Standard equalization mode
│   │   ├── callbacks.py
│   │   └── sliders_layout_generic.py
│   └── customized/                 # AI-powered processing modes
│       ├── customized_callbacks/
│       │   ├── AI_signal_processing.py
│       │   ├── process_sliders_callbacks.py
│       │   ├── Human_Ai_model_callbacks.py
│       │   ├── Musical_Ai_model_callbacks.py
│       │   └── Render_Ai_models_callbacks.py
│       └── customized_layouts/
│           └── ai_models_button.py
│
├── Utils/                           # Utility functions
│   ├── fft.py                      # FFT computation
│   ├── spectrogram.py              # Spectrogram generation
│   ├── Audiogram_scale.py          # Audiogram scaling utilities
│   ├── load_save_audio.py          # Audio file I/O
│   ├── Base_64_audio_converter.py  # Audio encoding/decoding
│   ├── Load_Human_Ai_model.py      # Human voice AI model loader
│   ├── Load_Musical_Ai_model.py    # Musical AI model loader
│   ├── multi_decoder_dprnn.py      # Audio separation decoder
│   ├── cine_viewers.py             # Visualization utilities
│   └── load_mode.py                # Mode configuration loader
│
├── Setting/                         # Configuration files
│   ├── generic_Frequency_Map.json
│   ├── Human_Voices_Frequency_Map.json
│   ├── Musical_Instruments_Frequency_Map.json
│   └── Animal_Sounds_Frequency_Map.json
│
└── assets/                          # Static assets
    ├── style.css                   # Custom styling
    └── how_to_use_fft.txt          # FFT usage guide
```

## How to Run

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:8050/`

### Requirements
The application uses the following key libraries:
- **Dash & Plotly**: Web framework and interactive visualizations
- **NumPy & SciPy**: Numerical and signal processing
- **PyTorch & Asteroid**: Deep learning and source separation
- **Demucs**: Audio decomposition
- **Soundfile**: Audio file handling

## Visualization Types

The application provides three main graph types for audio analysis:

### 1. **Frequency Domain Plot**
- Displays the frequency response of the audio signal
- Shows magnitude spectrum in both linear and logarithmic (dB) scales
- Supports audiogram scale visualization for specialized audio analysis
- Used for fine-tuning equalizer parameters

### 2. **Spectrogram (Time-Frequency Domain)**
- Heatmap visualization showing frequency content over time
- Uses a colorscale to represent signal intensity in dB
- Allows visualization of how frequency components evolve throughout the audio
- Essential for analyzing transient events and non-stationary signals

### 3. **Waveform Plot**
- Direct representation of the time-domain signal
- Used to visualize the raw audio waveform before and after processing
- Helps assess overall signal amplitude and clipping

These visualizations work together to provide comprehensive audio analysis and enable intuitive parameter adjustment.