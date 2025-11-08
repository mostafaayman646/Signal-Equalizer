"""
Layout Builder - Creates all UI components
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import json
import os


def load_mode_config(mode):
    """Load slider configs for a mode from JSON"""
    if mode == 'generic':
        return []  # Generic mode has dynamic sliders

    json_path = os.path.join(os.path.dirname(__file__), '..', 'modes', 'customized', 'frequency_maps.json')

    with open(json_path, 'r') as f:
        data = json.load(f)

    return data['modes'].get(mode, {}).get('sliders', [])


def create_app_layout():
    """Creates the main application layout"""

    return html.Div([
        # Stores
        dcc.Store(id='current-mode', data='instruments'),
        dcc.Store(id='signal-data-store'),
        dcc.Store(id='processed-signal-store'),
        dcc.Store(id='generic-subdivisions', data=[]),  # For generic mode

        # Navigation Bar (ONLY ONE)
        dbc.Navbar([
            dbc.Container([
                dbc.NavbarBrand([
                    html.I(className="fas fa-music me-2"),
                    "SIGNAL EQUALIZER ",
                    html.Span("PRO", style={'color': '#00d9ff', 'fontWeight': 'bold'})
                ]),

                dbc.Nav([
                    dcc.Dropdown(
                        id='mode-selector',
                        options=[
                            {'label': '🎸 Musical Instruments', 'value': 'instruments'},
                            {'label': '🐾 Animal Sounds', 'value': 'animals'},
                            {'label': '🗣️ Human Voices', 'value': 'voices'},
                            {'label': '⚙️ Generic Mode', 'value': 'generic'},
                        ],
                        value='instruments',
                        clearable=False,
                        style={'width': '250px', 'color': '#000'}
                    )
                ], className="ms-auto")
            ], fluid=True)
        ], color="dark", dark=True, className="mb-3"),

        # Main Content Container
        dbc.Container([
            dbc.Row([
                # Sidebar (LEFT)
                dbc.Col([
                    create_sidebar()
                ], width=2, className="sidebar"),

                # Main Content (RIGHT)
                dbc.Col([
                    create_main_content()
                ], width=10)
            ])
        ], fluid=True),

        # Hidden Audio Players
        # html.Audio(id='audio-player-before', controls=False, style={'display': 'none'}),
        # html.Audio(id='audio-player-after', controls=False, style={'display': 'none'}),

    ], style={'backgroundColor': '#1a1d2e', 'minHeight': '100vh'})


def create_sidebar():
    """Creates sidebar with controls"""

    return html.Div([
        # Upload
        html.H6("UPLOAD SIGNAL", style={'color': '#a0a4b8', 'fontSize': '0.8rem', 'marginBottom': '1rem'}),
        dcc.Upload(
            id='upload-signal',
            children=html.Div([
                html.I(className="fas fa-upload"),
                html.Span(" Select File", style={'marginLeft': '8px'})
            ]),
            style={
                'width': '100%',
                'padding': '1rem',
                'border': '2px dashed #00d9ff',
                'borderRadius': '8px',
                'textAlign': 'center',
                'cursor': 'pointer',
                'backgroundColor': '#252837',
                'color': '#fff'
            }
        ),

        html.Hr(style={'borderColor': '#2d3142'}),

        # Spectrograms Toggle
        html.H6("DISPLAY", style={'color': '#a0a4b8', 'fontSize': '0.8rem', 'marginTop': '2rem'}),
        dbc.Checklist(
            id='spectrogram-toggle',
            options=[{'label': ' Show Spectrograms', 'value': 'show'}],
            value=['show'],
            switch=True,
            style={'color': '#fff'}
        ),

        html.Hr(style={'borderColor': '#2d3142'}),

        # Audio Playback
        # html.H6("AUDIO", style={'color': '#a0a4b8', 'fontSize': '0.8rem', 'marginTop': '2rem'}),
        # dbc.Button([html.I(className="fas fa-play me-2"), "Play Original"],
        #            id='play-before', color="primary", size="sm", className="w-100 mb-2"),
        # dbc.Button([html.I(className="fas fa-play me-2"), "Play Processed"],
        #            id='play-after', color="success", size="sm", className="w-100"),
        # Audio Playback
        html.H6("AUDIO", style={'color': '#a0a4b8', 'fontSize': '0.8rem', 'marginTop': '2rem'}),

        # Original Audio
        dbc.Button([html.I(className="fas fa-upload me-2"), "Load Original"],
                   id='load-before', color="primary", outline=True, size="sm", className="w-100 mb-2"),
        html.Audio(id='audio-player-before', controls=True, style={'width': '100%'}),

        # Processed Audio
        dbc.Button([html.I(className="fas fa-upload me-2"), "Load Processed"],
                   id='load-after', color="success", outline=True, size="sm", className="w-100 mb-2 mt-3"),
        html.Audio(id='audio-player-after', controls=True, style={'width': '100%'}),

        html.Hr(style={'borderColor': '#2d3142'}),

        # Download
        html.H6("EXPORT", style={'color': '#a0a4b8', 'fontSize': '0.8rem', 'marginTop': '2rem'}),
        dbc.Button([html.I(className="fas fa-download me-2"), "Download"],
                   id='download-audio-btn', color="info", size="sm", className="w-100"),
        dcc.Download(id="download-processed-audio"),

    ], style={'padding': '1.5rem', 'backgroundColor': '#1e2230', 'height': '100vh'})


def create_main_content():
    """Creates main content area with graphs and sliders"""

    return html.Div([
        # Time Domain Graphs
        html.H5("TIME DOMAIN", style={'color': '#a0a4b8', 'fontSize': '0.9rem', 'marginBottom': '1rem'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='time-domain-pre', config={'displayModeBar': False},
                         style={'height': '200px', 'backgroundColor': '#161821', 'borderRadius': '8px'})
            ], width=10),
            dbc.Col([
                dcc.Graph(id='spectrogram-pre', config={'displayModeBar': False},
                         style={'height': '200px', 'backgroundColor': '#161821', 'borderRadius': '8px'})
            ], width=2, id='spectrogram-pre-col')
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='time-domain-post', config={'displayModeBar': False},
                         style={'height': '200px', 'backgroundColor': '#161821', 'borderRadius': '8px'})
            ], width=10),
            dbc.Col([
                dcc.Graph(id='spectrogram-post', config={'displayModeBar': False},
                         style={'height': '200px', 'backgroundColor': '#161821', 'borderRadius': '8px'})
            ], width=2, id='spectrogram-post-col')
        ], className="mb-3"),

        # Playback Controls
        dbc.ButtonGroup([
            dbc.Button(html.I(className="fas fa-play"), id='play-btn', size="sm", outline=True),
            dbc.Button(html.I(className="fas fa-pause"), id='pause-btn', size="sm", outline=True),
            dbc.Button(html.I(className="fas fa-stop"), id='stop-btn', size="sm", outline=True),
        ], className="mb-3"),

        # Frequency Domain
        html.H5("FREQUENCY DOMAIN", style={'color': '#a0a4b8', 'fontSize': '0.9rem', 'marginTop': '2rem', 'marginBottom': '1rem'}),
        dbc.Row([
            dbc.Col([]),
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("Linear", id='scale-linear', size="sm", color="primary", active=True),
                    dbc.Button("Audiogram", id='scale-audiogram', size="sm", outline=True),
                ])
            ], width="auto", className="text-end")
        ]),
        dcc.Graph(id='frequency-domain', config={'displayModeBar': False},
                 style={'height': '300px', 'backgroundColor': '#161821', 'borderRadius': '8px'}),

        # Mode-specific content container
        html.Div(id='mode-content-area')

    ], style={'padding': '2rem'})


def create_customized_sliders_area():
    """Creates the sliders area for customized modes"""
    return html.Div([
        html.H5("EQUALIZER", style={'color': '#a0a4b8', 'fontSize': '0.9rem', 'marginTop': '2rem', 'marginBottom': '1rem'}),
        html.Div(id='sliders-container', style={
            'display': 'flex',
            'justifyContent': 'space-around',
            'padding': '2rem',
            'backgroundColor': '#252837',
            'borderRadius': '8px'
        })
    ])


# def create_generic_controls_area():
#     """Creates the controls area for generic mode"""
#     from modes.generic.layout import create_generic_ui
#     return create_generic_ui()


def create_slider(slider_config):
    """Creates a single equalizer slider"""

    return html.Div([
        dcc.Slider(
            id={'type': 'equalizer-slider', 'index': slider_config['id']},
            min=0,
            max=2,
            step=0.1,
            value=1,
            vertical=True,
            verticalHeight=150,
            marks={0: '0', 1: '1', 2: '2'},
            tooltip={"placement": "right"}
        ),
        html.Div([
            html.I(className=slider_config['icon'], style={'fontSize': '2rem', 'color': '#00d9ff'})
        ], style={'textAlign': 'center', 'marginTop': '1rem'}),
        html.Label(slider_config['label'], style={
            'textAlign': 'center',
            'color': '#fff',
            'fontSize': '0.85rem',
            'marginTop': '0.5rem'
        })
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})