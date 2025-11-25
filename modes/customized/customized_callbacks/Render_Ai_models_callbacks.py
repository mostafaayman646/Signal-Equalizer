# import os
# import sys
#
# current = os.path.abspath(__file__)
# while not os.path.exists(os.path.join(current, 'assets')):
#     current = os.path.dirname(current)
# if current not in sys.path:
#     sys.path.insert(0, current)
#
# from dash import Output, Input
# from modes.customized.customized_layouts.ai_models_button import create_ai_interface
#
#
# def register_ai_models(app):
#     @app.callback(
#         Output('ai_models', 'children'),
#         Input('mode-selector', 'value')
#     )
#     def render_ai_interface(mode):
#         """
#         Renders the AI interface with a unique prefix based on mode.
#         """
#         if mode == 'Musical_Instruments':
#             # Ensure your Musical callback file uses 'musical-ai-' prefix!
#             # Or stick to 'ai-' if you don't want to edit the music callback file.
#             # For now, let's assume you keep 'ai' for music to avoid breaking it.
#             return create_ai_interface(id_prefix="ai")
#
#         elif mode == 'Human_Voices':
#             # Uses 'human-ai-' prefix to match the NEW human callback file
#             return create_ai_interface(id_prefix="human-ai")
#
#         else:
#             return []
"""
AI Models Rendering Callbacks
Updated for tab-based layout
"""

import os
import sys
from modes.customized.customized_layouts.ai_models_button import create_ai_tab_content
current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)
if current not in sys.path:
    sys.path.insert(0, current)

from dash import Output, Input, no_update, html


def register_ai_models(app):
    """
    Register AI button visibility based on mode
    Note: AI content is now always available in AI tab,
    but this controls which AI model to use
    """

    @app.callback(
        # Output('ai-equalizer-btn', 'children'),
        Output("ai-tab-wrapper",'children'),
        # Output('ai-equalizer-btn', 'disabled'),
        Input('mode-selector', 'value'),

        prevent_initial_call=False
    )
    def update_ai_button(mode):
        """
        Update AI button based on selected mode
        """

        if mode == 'Musical_Instruments':

            # return [
            #     html.I(className="fas fa-music me-2"),
            #     "Separate Musical Instruments"
            # ], False
            return create_ai_tab_content("ai")

        elif mode == 'Human_Voices':
            # return [
            #     html.I(className="fas fa-microphone me-2"),
            #     "Separate Human Voices"
            # ], False
            return create_ai_tab_content("human-ai")

        else:
            # return [
            #     html.I(className="fas fa-robot me-2"),
            #     "Start AI Separation"
            # ], False
            return create_ai_tab_content(is_supported=False)
