"""
Standalone test harness for the cine viewer.
Run with:  python standalone_cine_demo.py
"""

import numpy as np
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

from Utils.cine_viewers import CineViewer

# Generate more viewable synthetic test data

SAMPLE_RATE = 44_100
DURATION = 6.0  # seconds
t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)

# Frequencies: bass (50Hz), low (220Hz), mid (440Hz), high (1kHz), treble (5kHz)
freqs = [50, 220, 440, 1000, 5000]
amplitudes = [0.8, 0.6, 0.4, 0.3, 0.2]  # Balanced for visibility

# Base signal: sum of sines with subtle fade envelope for realism
envelope = 1 - 0.2 * np.sin(np.pi * t / DURATION)**2  # Gentle fade-in/out
original_signal = envelope * sum(
    a * np.sin(2 * np.pi * f * t) for f, a in zip(freqs, amplitudes)
)

# Processed: Boost highs (treble/mid), cut bass for clear "equalized" difference
process_factors = [0.5, 0.8, 1.2, 1.5, 2.0]  # Cut bass, boost highs
processed_signal = envelope * sum(
    factor * a * np.sin(2 * np.pi * f * t) for (f, a), factor in zip(zip(freqs, amplitudes), process_factors)
)

# Scale up for better visibility (peaks ~±2.5)
scale_factor = 2.0
original_signal *= scale_factor
processed_signal *= scale_factor

# Dash stores expect JSON-serialisable payloads -> convert to lists
signal_store_payload = {
    "samples": original_signal.tolist(),
    "sample_rate": SAMPLE_RATE
}
processed_store_payload = {
    "samples": processed_signal.tolist(),
    "sample_rate": SAMPLE_RATE
}

# App setup
external_stylesheets = [dbc.themes.DARKLY, dbc.icons.FONT_AWESOME]
app = Dash(__name__, external_stylesheets=external_stylesheets)

cine = CineViewer(namespace="cine-test")

app.layout = dbc.Container([
    html.H2("Cine Viewer Demo", className="mt-3 text-center"),
    html.P([
        "Synthetic multi-tone signal (50Hz bass + harmonics). ",
        "IN: Original mix. OUT: Highs boosted, bass cut. ",
        "Test: Play ▶️, zoom/drag (x/y), speed adjust, reset with ⏹️ or 🔄."
    ], className="text-muted text-center"),
    cine.layout(),
    dcc.Store(id="signal-data-store", data=signal_store_payload),
    dcc.Store(id="processed-signal-store", data=processed_store_payload),
], fluid=True, className="p-4", style={"backgroundColor": "#1a1a1a"})

cine.register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, port=8050)