"""
Layout Builder - Creates all UI components
(REDESIGNED with Card-Based Layout)
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import json
import os

from Utils.cine_viewers import CineViewer
cine_viewer = CineViewer(namespace="cine")

def load_mode_config(mode):
    """Load slider configs for a mode from JSON"""
    # Define the modes that have dedicated files
    file_based_modes = ['Musical_Instruments', 'Animal_Sounds', 'Human_Voices']

    if mode in file_based_modes:
        # Dynamically create filename based on mode
        json_filename = f"../Setting/{mode}_Frequency_Map.json"
        json_path = os.path.join(os.path.dirname(__file__), json_filename)
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Frequency map file not found at {json_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {json_path}")
            return {}
    
    elif mode == 'generic':
        # Generic mode has no sliders/map
        return {}
    else:
        # Handle other potential modes or error
        print(f"Warning: No frequency map defined for mode '{mode}'.")
        return {}
    
    # Data is now the root object for that mode, access 'sliders' directly
    return data.get('sliders', [])

def create_app_layout():
    """Creates the main application layout"""

    return html.Div([
        # Stores
        dcc.Store(id='current-mode', data='Musical_Instruments'),
        dcc.Store(id='signal-data-store'),
        dcc.Store(id='processed-signal-store'),
        dcc.Store(id='generic-subdivisions', data=[]),  # For generic mode

        # Navigation Bar
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
                            {'label': '🎸 Musical Instruments', 'value': 'Musical_Instruments'},
                            {'label': '🐾 Animal Sounds', 'value': 'Animal_Sounds'},
                            {'label': '🗣️ Human Voices', 'value': 'Human_Voices'},
                            {'label': '⚙️ Generic Mode', 'value': 'generic'},
                        ],
                        value='Musical_Instruments',
                        clearable=False,
                        style={'width': '250px', 'color': '#000'}
                    )
                ], className="ms-auto")
            ], fluid=True)
        ], color="dark", dark=True),

        # Main Content Container (Single Column)
        dbc.Container(fluid=True, className="main-app-content", children=[
            create_content_layout()
        ]),

    ], style={'backgroundColor': '#1a1d2e', 'minHeight': '100vh'})


def create_content_layout():
    """Creates the main content area with stacked cards"""

    return html.Div([
        # Row 1: Control Deck (Replaces Sidebar)
        create_control_deck(),

        # Row 2: Time Domain Graphs
        # html.Div([
        #     html.H5("TIME DOMAIN", className="section-heading"),
        #     dcc.Graph(
        #         id='time-domain-pre', config={'displayModeBar': False},
        #         style={'height': '200px', 'backgroundColor': '#161821', 'borderRadius': '8px', 'marginBottom': '1rem'}
        #     ),
        #     dcc.Graph(
        #         id='time-domain-post', config={'displayModeBar': False},
        #         style={'height': '200px', 'backgroundColor': '#161821', 'borderRadius': '8px'}
        #     )
        # ], className="app-card"),

        html.Div(
            cine_viewer.layout(),
            className="app-card"
        ),

        # Row 3: Spectrograms Section
        html.Div([
            html.H5("SPECTROGRAMS", className="section-heading"),
            dbc.Row([
                dbc.Col([
                    html.Div("Original Signal", style={'color': '#a0a4b8', 'fontSize': '0.8rem', 'marginBottom': '0.5rem', 'textAlign': 'center'}),
                    dcc.Graph(id='spectrogram-pre', config={'displayModeBar': False},
                             style={'height': '300px', 'backgroundColor': '#161821', 'borderRadius': '8px'})
                ], width=6, id='spectrogram-pre-col'),
                dbc.Col([
                    html.Div("Processed Signal", style={'color': '#a0a4b8', 'fontSize': '0.8rem', 'marginBottom': '0.5rem', 'textAlign': 'center'}),
                    dcc.Graph(id='spectrogram-post', config={'displayModeBar': False},
                             style={'height': '300px', 'backgroundColor': '#161821', 'borderRadius': '8px'})
                ], width=6, id='spectrogram-post-col')
            ])
        ], className="app-card"),

        # Row 4: Frequency Domain
        html.Div([
            dbc.Row([
                dbc.Col(html.H5("FREQUENCY DOMAIN", className="section-heading"), width=True),
                dbc.Col(
                    dbc.ButtonGroup([
                        dbc.Button("Linear", id='scale-linear', size="sm", color="primary", active=True),
                        dbc.Button("Audiogram", id='scale-audiogram', size="sm", outline=True, color="primary"),
                    ]), width="auto"
                )
            ], align="center", className="mb-3"),
            
            dcc.Graph(id='frequency-domain', config={'displayModeBar': False},
                     style={'height': '300px', 'backgroundColor': '#161821', 'borderRadius': '8px'}),
        
        ], className="app-card"),

        # Row 5: Mode-specific content container (Equalizer)
        html.Div(id='mode-content-area')
    ])


def create_control_deck():
    """Creates the top control deck card, replacing the old sidebar"""
    
    return html.Div([
        dbc.Row([
            # Column 1: Upload
            dbc.Col([
                html.H6("UPLOAD SIGNAL", className="sidebar-heading"),
                dcc.Upload(
                    id='upload-signal',
                    children=html.Div([
                        html.I(className="fas fa-upload me-2"),
                        html.Span(" Drag and Drop or Select File")
                    ]),
                    className="upload-box" # Use existing style
                )
            ], width=12, md=4, className="mb-3 mb-md-0"),

            # Column 2: Playback
            dbc.Col([
                html.H6("PLAYBACK", className="sidebar-heading"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button([html.I(className="fas fa-upload me-2"), "Load Original"],
                                   id='load-before', color="primary", outline=True, size="sm", className="w-100 mb-2"),
                        html.Audio(id='audio-player-before', controls=True, style={'width': '100%'})
                    ], width=6),
                    dbc.Col([
                        dbc.Button([html.I(className="fas fa-upload me-2"), "Load Processed"],
                                   id='load-after', color="success", outline=True, size="sm", className="w-100 mb-2"),
                        html.Audio(id='audio-player-after', controls=True, style={'width': '100%'})
                    ], width=6),
                ])
            ], width=12, md=5, className="mb-3 mb-md-0"),

            # Column 3: Display & Export
            dbc.Col([
                html.H6("DISPLAY & EXPORT", className="sidebar-heading"),
                dbc.Checklist(
                    id='spectrogram-toggle',
                    options=[{'label': ' Show Spectrograms', 'value': 'show'}],
                    value=['show'],
                    switch=True,
                    style={'color': '#fff'},
                    className="mb-3"
                ),
                dbc.Button([html.I(className="fas fa-download me-2"), "Download Processed Audio"],
                           id='download-audio-btn', color="info", size="sm", className="w-100"),
                dcc.Download(id="download-processed-audio"),
            ], width=12, md=3),
        ])
    ], className="app-card")


def create_customized_sliders_area():
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