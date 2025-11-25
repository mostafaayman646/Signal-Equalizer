import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

# Add this!
if current not in sys.path:
    sys.path.insert(0, current)

from dash import Input, Output
from components.layout_builder import create_slider
from Utils.load_mode import load_mode_config
# from modes.customized.sliders_layout_customized import create_customized_sliders_area
# from modes.generic.sliders_layout_generic import create_generic_controls_area
from components.layouts.Create_Sliders_Area import create_sliders_area

def register_mode_switch(app):
    @app.callback(
        Output('mode-content-area', 'children'),
        Output('sliders-container', 'children'),
        Output('current-mode', 'data'),
        Input('mode-selector', 'value')
    )
    def switch_mode_content(mode):
        """Switches mode content (sliders or generic controls)"""

        slider_configs = load_mode_config(mode)

        # if mode == 'generic':
        sliders_area = create_sliders_area()
        sliders = [create_slider(config) for config in slider_configs]
        # content = create_generic_controls_area()

        # else:
        #     sliders_area = create_customized_sliders_area()
        #     sliders = [create_slider(config) for config in slider_configs]
        #     content = create_customized_sliders_area()

        print(f"✓ Switched to {mode} mode")

        return sliders_area, sliders,mode

# import os
# import sys
#
# current = os.path.abspath(__file__)
# while not os.path.exists(os.path.join(current, 'assets')):
#     current = os.path.dirname(current)
#
# # Add this!
# if current not in sys.path:
#     sys.path.insert(0, current)
#
# from dash import Input, Output
# from components.layout_builder import create_slider
# from Utils.load_mode import load_mode_config
#
# def register_mode_switch(app):
#     @app.callback(
#         Output('sliders-container', 'children'),
#         Output('current-mode', 'data'),
#         Input('mode-selector', 'value')
#     )
#     def switch_mode_content(mode):
#         """Switches mode content (sliders only - no mode-content-area)"""
#
#         slider_configs = load_mode_config(mode)
#         sliders = [create_slider(config) for config in slider_configs]
#
#         print(f"✓ Switched to {mode} mode")
#
#         return sliders, mode