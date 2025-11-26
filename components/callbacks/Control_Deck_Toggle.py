"""
Control Deck Toggle Callback
Handles showing/hiding the control deck to save space
"""

from dash import Input, Output, State


def register_control_deck_toggle(app):
    """Register callback for collapsible control deck"""

    @app.callback(
        Output('control-deck-container', 'className'),
        Output('control-deck-icon', 'className'),
        Output('control-deck-visible', 'data'),
        Input('control-deck-toggle', 'n_clicks'),
        State('control-deck-visible', 'data'),
        prevent_initial_call=False
    )
    def toggle_control_deck(n_clicks, is_visible):
        """Toggle control deck visibility"""

        if n_clicks is None:
            # Initial state - hidden
            return (
                'control-deck-container hidden',
                'fas fa-chevron-down',
                False
            )

        # Toggle visibility
        new_state = not is_visible

        if new_state:
            return (
                'control-deck-container visible',
                'fas fa-chevron-up',
                True
            )
        else:
            return (
                'control-deck-container hidden',
                'fas fa-chevron-down',
                False
            )