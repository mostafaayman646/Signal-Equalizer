import dash
import dash_bootstrap_components as dbc

# Import NEW cine viewer callbacks
from components.callbacks.Cine_Viewer_Full import register_cine_viewer_callbacks

# Import other components and callbacks
from components.layout_builder import create_app_layout
from components.tab_callbacks import register_tab_callbacks
from components.callbacks.Upload_signal import register_Upload_signal
from components.callbacks.NavBar_Mode_Switch import register_mode_switch
from components.callbacks.Toggle_spectogram import register_Toggle_spectogram
from components.callbacks.PlayAudio import register_PlayAudio
from components.callbacks.Download_Audio import register_Download_audio
from components.callbacks.Scale_toggle import register_Scale_toggle
from modes.customized.customized_callbacks.process_sliders_callbacks import register_customized_callbacks
from modes.customized.customized_callbacks.Render_Ai_models_callbacks import register_ai_models
from modes.customized.customized_callbacks.Musical_Ai_model_callbacks import register_Musical_AiModel
from modes.customized.customized_callbacks.Human_Ai_model_callbacks import register_Human_AiModel
from modes.generic import register_generic_callbacks
from modes.customized.customized_callbacks.AI_signal_processing import register_ai_signal_processing
from components.callbacks.Control_Deck_Toggle import register_control_deck_toggle

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

# Register callbacks in correct order
register_tab_callbacks(app)
register_control_deck_toggle(app)

# NEW: Register enhanced cine viewer
register_cine_viewer_callbacks(app)

# Register other callbacks
register_Upload_signal(app)
register_mode_switch(app)
register_Toggle_spectogram(app)
register_PlayAudio(app)
register_Download_audio(app)
register_Scale_toggle(app)
register_customized_callbacks(app)
register_ai_models(app)
register_Musical_AiModel(app)
register_Human_AiModel(app)
register_generic_callbacks(app)
register_ai_signal_processing(app)

if __name__ == '__main__':
    # print("=" * 70)
    # print("🎵 SIGNAL EQUALIZER PRO - ENHANCED CINE VIEWER")
    # print("=" * 70)
    # print("\n🌐 Server: http://localhost:8050")
    # print("\n✨ New Features:")
    # print("   • Full signal display on both graphs")
    # print("   • Synchronized zooming and panning")
    # print("   • Moving playback cursor")
    # print("   • Audio source selection (Before/After)")
    # print("   • Click to seek position")
    # print("\n" + "=" * 70 + "\n")

    app.run(debug=True, port=8050)