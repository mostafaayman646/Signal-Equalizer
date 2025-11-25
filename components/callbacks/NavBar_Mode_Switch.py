import os
import sys
current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)
if current not in sys.path:
    sys.path.insert(0, current)
from dash import Input, Output, State
from components.layout_builder import create_slider
from Utils.load_mode import load_mode_config
from components.layouts.Create_Sliders_Area import create_sliders_area

def register_mode_switch(app):
    # NEW: Callback to initialize sliders on page load
    @app.callback(
        Output('sliders-container', 'children', allow_duplicate=True),
        Output('current-mode', 'data', allow_duplicate=True),
        Input('sliders-container', 'id'),  # Triggers on component mount
        State('mode-selector', 'value'),
        prevent_initial_call='initial_duplicate'  # Fixed: allows initial call with duplicates
    )
    def initialize_sliders(_, mode):
        """Initialize sliders when the app first loads"""
        if mode is None:
            mode = 'musical_instruments'  # Default mode
        slider_configs = load_mode_config(mode)
        sliders = [create_slider(config) for config in slider_configs]
        print(f"✓ Initialized {mode} mode with {len(sliders)} sliders")
        return sliders, mode
    
    # EXISTING: Callback for mode switching
    @app.callback(
        Output('mode-content-area', 'children'),
        Output('sliders-container', 'children'),
        Output('current-mode', 'data'),
        # Clear existing stores that are in ALL layouts
        Output('signal-data-store', 'data', allow_duplicate=True),
        Output('frequency-domain-data', 'data', allow_duplicate=True),
        Output('processed-signal-store', 'data', allow_duplicate=True),
        Output('generic-subdivisions', 'data', allow_duplicate=True),
        Output('slider-sync-store', 'data', allow_duplicate=True),
        # Clear visual components that exist in ALL layouts
        Output('upload-signal', 'contents'),
        Output('upload-signal', 'filename'),
        Output('spectrogram-pre', 'figure', allow_duplicate=True),
        Output('spectrogram-post', 'figure', allow_duplicate=True),
        Output('frequency-domain', 'figure', allow_duplicate=True),
        Output('cine-graph-pre', 'figure', allow_duplicate=True),
        Output('cine-graph-post', 'figure', allow_duplicate=True),
        Input('mode-selector', 'value'),
        prevent_initial_call=True
    )
    def switch_mode_content(mode):
        """Switches mode content (sliders or generic controls) and clears all data"""
        slider_configs = load_mode_config(mode)
        sliders_area = create_sliders_area()
        sliders = [create_slider(config) for config in slider_configs]
        
        print(f"✓ Switched to {mode} mode - ALL DATA CLEARED")
        
        return (
            sliders_area, 
            sliders, 
            mode,
            None,  # Clear signal-data-store
            None,  # Clear frequency-domain-data
            None,  # Clear processed-signal-store
            None,  # Clear generic-subdivisions
            None,  # Clear slider-sync-store
            None,  # Clear upload-signal contents
            None,  # Clear upload-signal filename
            {},    # Clear spectrogram-pre figure
            {},    # Clear spectrogram-post figure
            {},    # Clear frequency-domain figure
            {},    # Clear cine-graph-pre figure
            {},    # Clear cine-graph-post figure
        )