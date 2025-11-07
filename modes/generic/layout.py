from components.base_template import (
    create_base_layout,
    create_generic_mode_additions
)
from dash import html, dcc
import dash_bootstrap_components as dbc

# Generic mode starts with no sliders - they're added dynamically
slider_configs = []

# Additional components for generic mode
additional_components = create_generic_mode_additions()

# You can also add more custom components
additional_components.extend([
    html.Div([
        html.H6("Subdivision Configuration", className="mt-3"),
        html.Div(id='subdivision-configs', children=[
            # Dynamic subdivisions will be added here
        ])
    ], className="p-3 border rounded mt-3")
])

# Create layout using base template
layout = create_base_layout(
    slider_configs=slider_configs,
    mode_name="Generic Mode",
    additional_components=additional_components
)


# ============================================================================
# Example: Adding a custom subdivision component for generic mode
# ============================================================================

def create_subdivision_component(subdivision_id, start_freq=0, end_freq=1000):
    """
    Creates a subdivision control component for generic mode.
    This would be dynamically added when user clicks "Add Subdivision".
    """
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Start Frequency (Hz):"),
                        dcc.Input(
                            id=f'start-freq-{subdivision_id}',
                            type='number',
                            value=start_freq,
                            className="form-control"
                        )
                    ], width=4),

                    dbc.Col([
                        html.Label("End Frequency (Hz):"),
                        dcc.Input(
                            id=f'end-freq-{subdivision_id}',
                            type='number',
                            value=end_freq,
                            className="form-control"
                        )
                    ], width=4),

                    dbc.Col([
                        html.Label("Scale:"),
                        dcc.Slider(
                            id=f'scale-{subdivision_id}',
                            min=0,
                            max=2,
                            step=0.1,
                            value=1,
                            marks={0: '0', 1: '1', 2: '2'}
                        )
                    ], width=3),

                    dbc.Col([
                        dbc.Button(
                            html.I(className="fas fa-trash"),
                            id=f'delete-{subdivision_id}',
                            color="danger",
                            size="sm",
                            className="mt-4"
                        )
                    ], width=1)
                ])
            ])
        ], className="mb-2")
    ], id=f'subdivision-{subdivision_id}')
