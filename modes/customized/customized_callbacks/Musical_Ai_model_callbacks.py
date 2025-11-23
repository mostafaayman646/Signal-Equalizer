from dash import html, dcc, callback, Output, Input, State, ALL, ctx, no_update
import os
import time
from Utils.Load_Musical_Ai_model import Audio_Seprator, Mix_Audio


def register_Musical_AiModel(app):
    # --- 1. SEPARATION CALLBACK ---
    @app.callback(
        [Output('ai-stems-store', 'data'),
         Output('ai-sliders-container', 'children'),
         Output('loading-status', 'children'),
         Output('ai-player-container', 'style')],
        Input('ai-equalizer-btn', 'n_clicks'),
        State('signal-data-store', 'data'),
        State('current-mode', 'data'),
        prevent_initial_call=True
    )
    def on_ai_equalizer_click(n_clicks, signal_data, mode):

        if not signal_data:
            return {}, [], "Error: No file loaded.", {'display': 'none'}

        file_path = signal_data.get('path')

        if not file_path or not os.path.exists(file_path):
            return {}, [], "Error: File path not found.", {'display': 'none'}

        if mode == 'Musical_Instruments':
            # This now saves files into 'static/separated'
            stems_map = Audio_Seprator(file_path)

            if not stems_map:
                return {}, [], "Error: AI Separation failed.", {'display': 'none'}

            sliders_ui = []
            for stem_name in stems_map.keys():
                sliders_ui.append(html.Div([
                    html.Label(f"{stem_name.upper()} Volume"),
                    dcc.Slider(
                        id={'type': 'ai-slider', 'index': stem_name},
                        min=0, max=2, step=0.1, value=1,
                        marks={0: 'Mute', 1: '100%', 2: 'Boost'},
                        updatemode='mouseup'
                    )
                ], style={'padding': '10px'}))

            return stems_map, sliders_ui, "AI Separation Complete!", {'display': 'block'}

        return {}, [], "Mode not supported yet.", {'display': 'none'}

    # --- 2. MIXING CALLBACK ---
    @app.callback(
        Output('ai-audio-player', 'src'),
        Input({'type': 'ai-slider', 'index': ALL}, 'value'),
        State('ai-stems-store', 'data'),
        State({'type': 'ai-slider', 'index': ALL}, 'id'),
        prevent_initial_call=True
    )
    def update_ai_mix(slider_values, stems_paths, slider_ids):
        if not stems_paths:
            return no_update

        gains = {}
        for val, id_dict in zip(slider_values, slider_ids):
            gains[id_dict['index']] = val

        # This now saves to 'static/ai_mixed_output.wav'
        output_filename = Mix_Audio(stems_paths, gains)

        if not output_filename:
            return no_update

        # FIX: Serve from /static/ instead of /assets/
        # Dash/Flask automatically serves the 'static' folder at this URL
        return f"/static/{output_filename}?t={int(time.time())}"