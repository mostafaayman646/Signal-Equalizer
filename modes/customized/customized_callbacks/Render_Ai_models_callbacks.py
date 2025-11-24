import os
import sys

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
        Renders the AI interface with a unique prefix based on mode.
        """
        if mode == 'Musical_Instruments':
            # Ensure your Musical callback file uses 'musical-ai-' prefix!
            # Or stick to 'ai-' if you don't want to edit the music callback file.
            # For now, let's assume you keep 'ai' for music to avoid breaking it.
            return create_ai_interface(id_prefix="ai")

        elif mode == 'Human_Voices':
            # Uses 'human-ai-' prefix to match the NEW human callback file
            return create_ai_interface(id_prefix="human-ai")

        else:
            return []
