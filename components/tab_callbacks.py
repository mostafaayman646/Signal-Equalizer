"""
Tab Management Callbacks
Handles switching between Manual and AI modes
"""

from dash import Input, Output, State, callback_context


def register_tab_callbacks(app):
    """Register tab switching callbacks"""

    @app.callback(
        Output('manual-tab-wrapper', 'style'),
        Output('ai-tab-wrapper', 'style'),
        Output('tab-manual', 'className'),
        Output('tab-ai', 'className'),
        Output('active-tab', 'data'),
        Input('tab-manual', 'n_clicks'),
        Input('tab-ai', 'n_clicks'),
        State('active-tab', 'data'),
        prevent_initial_call=True
    )
    def switch_tabs(manual_clicks, ai_clicks, current_tab):
        """Switch between Manual and AI tabs using show/hide"""

        ctx = callback_context

        if not ctx.triggered:
            return (
                {'display': 'block'},
                {'display': 'none'},
                'mode-tab active',
                'mode-tab',
                'manual'
            )

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'tab-manual':
            return (
                {'display': 'block'},  # Show manual
                {'display': 'none'},  # Hide AI
                'mode-tab active',
                'mode-tab',
                'manual'
            )
        elif button_id == 'tab-ai':
            return (
                {'display': 'none'},  # Hide manual
                {'display': 'block'},  # Show AI
                'mode-tab',
                'mode-tab active',
                'ai'
            )

        # Default fallback
        return (
            {'display': 'block'},
            {'display': 'none'},
            'mode-tab active',
            'mode-tab',
            'manual'
        )