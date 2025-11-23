from dash import Input, Output

def register_Toggle_spectogram(app):
    @app.callback(
    Output('spectrogram-pre-col', 'style'),
    Output('spectrogram-post-col', 'style'),
    Input('spectrogram-toggle', 'value')
    )
    def toggle_spectrograms(value):
        """Show/hide spectrograms"""
        if value and 'show' in value:
            # Show with proper width for side-by-side layout
            return {'width': '50%'}, {'width': '50%'}
        # Hide spectrograms
        return {'display': 'none'}, {'display': 'none'}