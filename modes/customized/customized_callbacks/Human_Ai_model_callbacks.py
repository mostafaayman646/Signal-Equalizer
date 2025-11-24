from dash import html, dcc, callback, Output, Input, State, ALL, no_update
import os
import time
from Utils.Load_Human_Ai_model import Separate_Voices, Mix_Human_Audio


def register_Human_AiModel(app):
    # --- 1. SEPARATION CALLBACK (Human) ---
    @app.callback(
        [Output('human-ai-stems-store', 'data'),
         Output('human-ai-sliders-container', 'children'),
         Output('human-ai-loading-status', 'children'),
         Output('human-ai-player-container', 'style')],
        Input('human-ai-equalizer-btn', 'n_clicks'),  # <--- Unique ID
        State('signal-data-store', 'data'),
        prevent_initial_call=True
    )
    def on_human_ai_click(n_clicks, signal_data):
        if not signal_data:
            return {}, [], "Error: No file loaded.", {'display': 'none'}

        file_path = signal_data.get('path')

        if not file_path or not os.path.exists(file_path):
            return {}, [], "Error: File path not found.", {'display': 'none'}

        # RUN ASTEROID MODEL
        stems_map = Separate_Voices(file_path)

        if not stems_map:
            return {}, [], "Error: Separation failed.", {'display': 'none'}

        # Generate Sliders
        sliders_ui = []
        for stem_name in stems_map.keys():
            display_name = stem_name.replace("_", " ").upper()
            sliders_ui.append(html.Div([
                html.Label(f"{display_name}"),
                dcc.Slider(
                    id={'type': 'human-ai-slider', 'index': stem_name},  # <--- Unique Pattern
                    min=0, max=2, step=0.1, value=1,
                    marks={0: 'Mute', 1: '100%', 2: 'Boost'},
                    updatemode='mouseup'
                )
            ], style={'padding': '10px'}))

        return stems_map, sliders_ui, "Separation Complete!", {'display': 'block'}

    # --- 2. MIXING CALLBACK (Human) ---
    @app.callback(
        Output('human-ai-audio-player', 'src'),  # <--- Unique Player
        Input({'type': 'human-ai-slider', 'index': ALL}, 'value'),
        State('human-ai-stems-store', 'data'),
        State({'type': 'human-ai-slider', 'index': ALL}, 'id'),
        prevent_initial_call=True
    )
    def update_human_mix(slider_values, stems_paths, slider_ids):
        if not stems_paths:
            return no_update

        gains = {}
        for val, id_dict in zip(slider_values, slider_ids):
            gains[id_dict['index']] = val

        # Mix and Save
        output_filename = Mix_Human_Audio(stems_paths, gains)

        if not output_filename:
            return no_update

        return f"/static/{output_filename}?t={int(time.time())}"