"""
AI Models Rendering Callbacks
Updated for tab-based layout
"""

import os
import sys
from modes.customized.customized_layouts.ai_models_button import create_ai_tab_content
# current = os.path.abspath(__file__)
# while not os.path.exists(os.path.join(current, 'assets')):
#     current = os.path.dirname(current)
# if current not in sys.path:
#     sys.path.insert(0, current)

from dash import Output, Input, no_update, html


def register_ai_models(app):
    """
    Register AI button visibility based on mode
    """

    @app.callback(
        Output("ai-tab-wrapper",'children'),
        Input('mode-selector', 'value'),
        prevent_initial_call=False
    )
    def update_ai_button(mode):
        """
        Update AI button based on selected mode
        """

        if mode == 'Musical_Instruments':
            return create_ai_tab_content("ai")

        elif mode == 'Human_Voices':
            return create_ai_tab_content("human-ai")

        else:
            return create_ai_tab_content(is_supported=False)
