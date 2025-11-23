from dash import html

def create_sliders_area():
    """Creates the sliders area for customized modes"""
    # This now gets placed inside the 'app-card' style automatically
    return html.Div([
        html.H5("EQUALIZER", className="section-heading"),
        html.Div(id='sliders-container', style={
            'display': 'flex',
            'justifyContent': 'space-around',
            'padding': '2rem 0',
        })
    ], className="app-card equalizer-section") # Re-use equalizer-section for consistent padding