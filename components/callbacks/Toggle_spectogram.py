from dash import Input, Output

def register_Toggle_spectogram(app):
    @app.callback(
        Output('spectrogram-row', 'style'),
        Input('spectrogram-toggle', 'value')
    )
    def toggle_spectrograms(value):
        """Show/hide spectrograms"""
        if value and 'show' in value:
            # Show spectrograms with proper width
            return {
                'display': 'grid',
                'gridTemplateColumns': '1fr 1fr',
                'gap': '0.5rem',
                'marginBottom': '0.5rem',
                'width': '100%'
            }
        # Hide spectrograms
        return {'display': 'none'}