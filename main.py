"""
Signal Equalizer Pro - Main Application
"""

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

# Import components and callbacks
from components.layout_builder import create_app_layout, cine_viewer
from components.main_callbacks import register_main_callbacks
from modes.customized.callbacks import register_customized_callbacks
# from modes.generic.callbacks import register_generic_callbacks

# Initialize App
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ],
    suppress_callback_exceptions=True
)

server = app.server

# Set main layout
app.layout = create_app_layout()

# Register callbacks
cine_viewer.register_callbacks(app)
register_main_callbacks(app)
register_customized_callbacks(app)  # For instruments, animals, voices
# register_generic_callbacks(app)      # For generic mode

if __name__ == '__main__':
    print("=" * 70)
    print("🎵 SIGNAL EQUALIZER PRO")
    print("=" * 70)
    print("\n📍 Server: http://localhost:8050")
    print("\n✨ Modes:")
    print("   • Musical Instruments")
    print("   • Animal Sounds")
    print("   • Human Voices")
    print("   • Generic Mode (custom subdivisions)")
    print("\n" + "=" * 70 + "\n")

    app.run(debug=True, port=8050)