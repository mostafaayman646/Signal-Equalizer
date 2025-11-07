
from components.base_template import create_base_layout
from dash import html
import dash_bootstrap_components as dbc

# Define slider configurations for human voices
slider_configs = [
    {
        'id': 'slider-male-1',
        'label': 'Male 1',
        'icon': 'fas fa-male',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-female-1',
        'label': 'Female 1',
        'icon': 'fas fa-female',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-child',
        'label': 'Child',
        'icon': 'fas fa-child',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-elderly',
        'label': 'Elderly',
        'icon': 'fas fa-user',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
]

# Additional component specific to voices mode
additional_components = [
    html.Div([
        html.H6("Voice Characteristics", className="mt-4"),
        dbc.Row([
            dbc.Col([
                html.Label("Age Group Filter:"),
                dbc.Checklist(
                    id='age-filter',
                    options=[
                        {'label': 'Young', 'value': 'young'},
                        {'label': 'Middle Age', 'value': 'middle'},
                        {'label': 'Elderly', 'value': 'elderly'},
                    ],
                    value=['young', 'middle', 'elderly'],
                    inline=True
                )
            ], width=6),
            dbc.Col([
                html.Label("Gender Filter:"),
                dbc.Checklist(
                    id='gender-filter',
                    options=[
                        {'label': 'Male', 'value': 'male'},
                        {'label': 'Female', 'value': 'female'},
                    ],
                    value=['male', 'female'],
                    inline=True
                )
            ], width=6),
        ])
    ], className="voice-filters p-3 border rounded")
]

# Create layout using base template with additional components
layout = create_base_layout(
    slider_configs=slider_configs,
    mode_name="Human Voices",
    additional_components=additional_components
)
