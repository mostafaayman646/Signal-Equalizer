import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

# Add this!
if current not in sys.path:
    sys.path.insert(0, current)

from dash import Output, Input
from modes.customized.customized_layouts.ai_models_button import create_ai_equalizer_button

def register_ai_models(app):
    @app.callback(
        Output('ai_models', 'children'),
        Input('mode-selector', 'value')
    )
    def render_ai_button(mode):
        """Renders the AI Equalizer button in the ai_models div"""
        
        if mode in ['Musical_Instruments', 'Human_Voices']:
            return create_ai_equalizer_button()
        else:
            return []