import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

# Add this!
if current not in sys.path:
    sys.path.insert(0, current)

from dash import Input, Output, State, callback_context, ALL
from dash.exceptions import PreventUpdate

from components.layouts.freq_fig import create_freq_figure

def register_Scale_toggle(app):
    @app.callback(
    Output('scale-linear', 'active'),
    Output('scale-audiogram', 'active'),
    Output('scale-linear', 'color'),
    Output('scale-audiogram', 'color'),
    Output('scale-linear', 'outline'),
    Output('scale-audiogram', 'outline'),
    Input('scale-linear', 'n_clicks'),
    Input('scale-audiogram', 'n_clicks'),
    prevent_initial_call=True
    )
    def toggle_scale(linear, audio):
        """Toggle frequency scale with proper visual feedback"""
        ctx = callback_context
        
        if not ctx.triggered:
            # Default state: Linear active
            return True, False, "primary", "secondary", False, True
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'scale-linear':
            # Linear is active
            return True, False, "primary", "secondary", False, True
        else:
            # Audiogram is active
            return False, True, "secondary", "primary", True, False

    @app.callback(
        Output('frequency-domain', 'figure', allow_duplicate=True),
        Input('scale-linear', 'n_clicks'),
        Input('scale-audiogram', 'n_clicks'),
        State('frequency-domain-data', 'data'),
        prevent_initial_call=True
    )
    def redraw_frequency_figure(linear_clicks, audiogram_clicks, freq_data):
        ctx = callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not freq_data:
            raise PreventUpdate

        freqs = freq_data.get('frequencies') or []
        mags = freq_data.get('magnitudes') or []
        if not freqs or not mags:
            raise PreventUpdate

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        scale_mode = 'linear' if button_id == 'scale-linear' else 'audiogram'

        return create_freq_figure(freqs, mags, use_db=True, scale_mode=scale_mode)