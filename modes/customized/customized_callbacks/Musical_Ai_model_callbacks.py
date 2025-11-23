import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

# Add this!
if current not in sys.path:
    sys.path.insert(0, current)

from dash import html, callback, Output, Input, State
from Utils.Load_Musical_Ai_model import Audio_Seprator

def register_Musical_AiModel(app):
    @app.callback(
        Output('ai-equalizer-btn', 'n_clicks'),
        Input('ai-equalizer-btn', 'n_clicks'),
        State('signal-data-store','data'),
        State('current-mode','data'),
        prevent_initial_call=True
    )
    def on_ai_equalizer_click(n_clicks,data,mode):
        """Handles the AI Equalizer button click"""
        if mode =='Musical_Instruments':
            # TODO: Implement AI Equalizer functionality
            Separated_Audios = Audio_Seprator(data)