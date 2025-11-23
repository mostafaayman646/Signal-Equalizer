import os
import sys

# Ensure assets folder can be found (standard boilerplate)
current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)
if current not in sys.path:
    sys.path.insert(0, current)

from dash import Output, Input
from modes.customized.customized_layouts.ai_models_button import create_ai_interface

def register_ai_models(app):
    @app.callback(
        Output('ai_models', 'children'),
        Input('mode-selector', 'value')
    )
    def render_ai_interface(mode):
        """
        If the user selects a supported mode, render the AI Button
        AND the hidden containers for sliders/storage.
        """
        if mode in ['Musical_Instruments', 'Human_Voices']:
            return create_ai_interface()
        else:
            return []