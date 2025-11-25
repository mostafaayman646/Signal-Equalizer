# """
# Layout Builder - Creates all UI components
# (REDESIGNED with Card-Based Layout)
# """
#
# from dash import html, dcc
# import dash_bootstrap_components as dbc
# import json
# import os
#
# from Utils.cine_viewers import CineViewer
# cine_viewer = CineViewer(namespace="cine")
#
# def create_app_layout():
#     """Creates the main application layout"""
#
#     return html.Div([
#         # Stores
#         dcc.Store(id='current-mode', data='Musical_Instruments'),
#         dcc.Store(id='signal-data-store'),
#         dcc.Store(id='processed-signal-store'),
#         dcc.Store(id='generic-subdivisions', data=[]),  # For generic mode
#
#         # Navigation Bar
#         dbc.Navbar([
#             dbc.Container([
#                 dbc.NavbarBrand([
#                     html.I(className="fas fa-music me-2"),
#                     "SIGNAL EQUALIZER ",
#                     html.Span("PRO", style={'color': '#00d9ff', 'fontWeight': 'bold'})
#                 ]),
#
#                 dbc.Nav([
#                     dcc.Dropdown(
#                         id='mode-selector',
#                         options=[
#                             {'label': '🎸 Musical Instruments', 'value': 'Musical_Instruments'},
#                             {'label': '🐾 Animal Sounds', 'value': 'Animal_Sounds'},
#                             {'label': '🗣️ Human Voices', 'value': 'Human_Voices'},
#                             {'label': '⚙️ Generic Mode', 'value': 'generic'},
#                         ],
#                         value='Musical_Instruments',
#                         clearable=False,
#                         style={'width': '250px', 'color': '#000'}
#                     )
#                 ], className="ms-auto")
#             ], fluid=True)
#         ], color="dark", dark=True),
#
#         # Main Content Container (Single Column)
#         dbc.Container(fluid=True, className="main-app-content", children=[
#             create_content_layout()
#         ]),
#
#     ], style={'backgroundColor': '#1a1d2e', 'minHeight': '100vh'})
#
#
# def create_content_layout():
#     """Creates the main content area with stacked cards"""
#
#     return html.Div([
#         # Row 1: Control Deck (Replaces Sidebar)
#         create_control_deck(),
#
#         html.Div(
#             cine_viewer.layout(),
#             className="app-card"
#         ),
#
#         # Row 3: Spectrograms Section
#         html.Div([
#             html.H5("SPECTROGRAMS", className="section-heading"),
#             dbc.Row([
#                 dbc.Col([
#                     html.Div("Original Signal", style={'color': '#a0a4b8', 'fontSize': '0.8rem', 'marginBottom': '0.5rem', 'textAlign': 'center'}),
#                     dcc.Graph(id='spectrogram-pre', config={'displayModeBar': False},
#                              style={'height': '600px', 'backgroundColor': '#161821', 'borderRadius': '8px'})
#                 ], width=6, id='spectrogram-pre-col'),
#                 dbc.Col([
#                     html.Div("Processed Signal", style={'color': '#a0a4b8', 'fontSize': '0.8rem', 'marginBottom': '0.5rem', 'textAlign': 'center'}),
#                     dcc.Graph(id='spectrogram-post', config={'displayModeBar': False},
#                              style={'height': '600px', 'backgroundColor': '#161821', 'borderRadius': '8px'})
#                 ], width=6, id='spectrogram-post-col')
#             ])
#         ], className="app-card"),
#
#         # Row 4: Frequency Domain
#         html.Div([
#             dbc.Row([
#                 dbc.Col(html.H5("FREQUENCY DOMAIN", className="section-heading"), width=True),
#                 dbc.Col(
#                     dbc.ButtonGroup([
#                         dbc.Button("Linear", id='scale-linear', size="sm", color="primary", active=True),
#                         dbc.Button("Audiogram", id='scale-audiogram', size="sm", outline=True, color="primary"),
#                     ]), width="auto"
#                 )
#             ], align="center", className="mb-3"),
#
#             dcc.Graph(id='frequency-domain', config={'displayModeBar': False},
#                      style={'height': '300px', 'backgroundColor': '#161821', 'borderRadius': '8px'}),
#
#         ], className="app-card"),
#
#         # Row 5: Mode-specific content container (Equalizer)
#         # html.Div(id='mode-content-area')
#         html.Div([
#         html.H5("EQUALIZER", className="section-heading"),
#         html.Div(id='sliders-container', style={
#             'display': 'flex',
#             'justifyContent': 'space-around',
#             'padding': '2rem 0',
#         })
#         ], className="app-card equalizer-section",id='mode-content-area'),
#
#         # Row 6: AI Models (placeholder for future use)
#         html.Div(id='ai_models'),
#     ])
#
#
#
#
# def create_control_deck():
#     """Creates the top control deck card"""
#
#     return html.Div([
#         dbc.Row([
#             # Column 1: Upload
#             dbc.Col([
#                 html.H6("UPLOAD SIGNAL", className="sidebar-heading"),
#                 dcc.Upload(
#                     id='upload-signal',
#                     children=html.Div([
#                         html.I(className="fas fa-upload me-2"),
#                         html.Span(" Drag and Drop or Select File")
#                     ]),
#                     className="upload-box" # Use existing style
#                 )
#             ], width=12, md=4, className="mb-3 mb-md-0"),
#
#             # Column 2: Playback
#             dbc.Col([
#                 html.H6("PLAYBACK", className="sidebar-heading"),
#                 dbc.Row([
#                     dbc.Col([
#                         dbc.Button([html.I(className="fas fa-upload me-2"), "Load Original"],
#                                    id='load-before', color="primary", outline=True, size="sm", className="w-100 mb-2"),
#                         html.Audio(id='audio-player-before', controls=True, style={'width': '100%'})
#                     ], width=6),
#                     dbc.Col([
#                         dbc.Button([html.I(className="fas fa-upload me-2"), "Load Processed"],
#                                    id='load-after', color="success", outline=True, size="sm", className="w-100 mb-2"),
#                         html.Audio(id='audio-player-after', controls=True, style={'width': '100%'})
#                     ], width=6),
#                 ])
#             ], width=12, md=5, className="mb-3 mb-md-0"),
#
#             # Column 3: Display & Export
#             dbc.Col([
#                 html.H6("DISPLAY & EXPORT", className="sidebar-heading"),
#                 dbc.Checklist(
#                     id='spectrogram-toggle',
#                     options=[{'label': ' Show Spectrograms', 'value': 'show'}],
#                     value=['show'],
#                     switch=True,
#                     style={'color': '#fff'},
#                     className="mb-3"
#                 ),
#                 dbc.Button([html.I(className="fas fa-download me-2"), "Download Processed Audio"],
#                            id='download-audio-btn', color="info", size="sm", className="w-100"),
#                 dcc.Download(id="download-processed-audio"),
#             ], width=12, md=3),
#         ])
#     ], className="app-card")
#
# def create_slider(slider_config):
#     """Creates a single equalizer slider"""
#
#     return html.Div([
#         dcc.Slider(
#             id={'type': 'equalizer-slider', 'index': slider_config['id']},
#             min=0,
#             max=2,
#             step=0.1,
#             value=1,
#             vertical=True,
#             verticalHeight=150,
#             marks={0: '0', 1: '1', 2: '2'},
#             tooltip={"placement": "right"}
#         ),
#         html.Div([
#             html.I(className=slider_config['icon'], style={'fontSize': '2rem', 'color': '#00d9ff'})
#         ], style={'textAlign': 'center', 'marginTop': '1rem'}),
#         html.Label(slider_config['label'], style={
#             'textAlign': 'center',
#             'color': '#fff',
#             'fontSize': '0.85rem',
#             'marginTop': '0.5rem'
#         })
#     ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
"""
Layout Builder - Tab-Based Design with Manual vs AI Modes
Compact, modern layout with synchronized controls
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

from Utils.cine_viewers import CineViewer

cine_viewer = CineViewer(namespace="cine")


def create_app_layout():
    """Creates the main application layout with tabs"""

    return html.Div([
        # Stores
        dcc.Store(id='current-mode', data='Musical_Instruments'),
        dcc.Store(id='signal-data-store'),
        dcc.Store(id='frequency-domain-data'),
        dcc.Store(id='processed-signal-store'),
        dcc.Store(id='generic-subdivisions', data=[]),
        dcc.Store(id='active-tab', data='manual'),
        dcc.Store(id='slider-sync-store'),

        # Navigation Bar
        create_navbar(),

        # Main Content Container
        dbc.Container(fluid=True, className="main-app-content", children=[
            # Control Deck (Always Visible)
            create_control_deck(),

            # Tab Selector
            create_tab_selector(),

            # Tab Content Container
            html.Div([
                # Manual Tab (Initially Visible)
                html.Div(create_manual_tab_content(), id='manual-tab-wrapper', style={'display': 'block'}),
                # AI Tab (Initially Hidden)
                html.Div(id='ai-tab-wrapper', style={'display': 'none'}),
            ], id='tab-content-container')
        ]),

    ], style={'backgroundColor': '#0a0e27', 'minHeight': '100vh'})


def create_navbar():
    """Creates the navigation bar"""
    return dbc.Navbar([
        dbc.Container([
            dbc.NavbarBrand([
                html.I(className="fas fa-waveform-lines me-2"),
                "SIGNAL EQUALIZER ",
                html.Span("PRO", className='brand-pro')
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
    ], className="navbar", dark=True)


def create_tab_selector():
    """Creates the tab selector pills"""
    return html.Div([
        html.Button([
            html.I(className="fas fa-sliders me-2"),
            "Manual Mode"
        ], id='tab-manual', className='mode-tab active'),

        html.Button([
            html.I(className="fas fa-robot me-2"),
            "AI Mode"
        ], id='tab-ai', className='mode-tab'),
    ], className='mode-tabs')


def create_control_deck():
    """Creates the compact control deck"""

    return html.Div([
        dbc.Row([
            # Column 1: Upload
            dbc.Col([
                html.Div([
                    html.I(className="fas fa-cloud-upload-alt",
                           style={'fontSize': '2rem', 'color': '#00d9ff', 'marginBottom': '0.5rem'}),
                    html.Div("UPLOAD SIGNAL", className="section-heading",
                             style={'paddingLeft': 0, 'marginBottom': '0.5rem'}),
                    dcc.Upload(
                        id='upload-signal',
                        children=html.Div([
                            html.Div("Drag & Drop", style={'fontWeight': 'bold', 'fontSize': '0.95rem'}),
                            html.Div("or click to select", style={'fontSize': '0.75rem', 'opacity': 0.7})
                        ]),
                        className="upload-box",
                        style={'padding': '1.5rem'}
                    )
                ], className='control-section')
            ], width=12, lg=4, className="mb-3"),

            # Column 2: Playback Controls
            dbc.Col([
                html.Div([
                    html.I(className="fas fa-headphones",
                           style={'fontSize': '2rem', 'color': '#00d9ff', 'marginBottom': '0.5rem'}),
                    html.Div("PLAYBACK", className="section-heading",
                             style={'paddingLeft': 0, 'marginBottom': '0.5rem'}),
                    dbc.ButtonGroup([
                        dbc.Button([html.I(className="fas fa-play me-1"), "Original"],
                                   id='load-before', color="primary", size="sm"),
                        dbc.Button([html.I(className="fas fa-waveform-lines me-1"), "Processed"],
                                   id='load-after', color="success", size="sm"),
                    ], className="w-100 mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Audio(id='audio-player-before', controls=True,
                                       style={'width': '100%', 'height': '35px'})
                        ], width=6),
                        dbc.Col([
                            html.Audio(id='audio-player-after', controls=True,
                                       style={'width': '100%', 'height': '35px'})
                        ], width=6),
                    ])
                ], className='control-section')
            ], width=12, lg=4, className="mb-3"),

            # Column 3: Display & Export
            dbc.Col([
                html.Div([
                    html.I(className="fas fa-cog",
                           style={'fontSize': '2rem', 'color': '#00d9ff', 'marginBottom': '0.5rem'}),
                    html.Div("OPTIONS", className="section-heading",
                             style={'paddingLeft': 0, 'marginBottom': '0.5rem'}),
                    dbc.Checklist(
                        id='spectrogram-toggle',
                        options=[{'label': ' Show Spectrograms', 'value': 'show'}],
                        value=['show'],
                        switch=True,
                        className="mb-2"
                    ),
                    dbc.Button([html.I(className="fas fa-download me-2"), "Export"],
                               id='download-audio-btn', color="info", size="sm", className="w-100"),
                    dcc.Download(id="download-processed-audio"),
                ], className='control-section')
            ], width=12, lg=4, className="mb-3"),
        ])
    ], className="app-card")


def create_manual_tab_content():
    """Creates the manual mode tab content"""

    return html.Div([
        # Cine Viewer (Time Domain)
        html.Div(cine_viewer.layout(), className="app-card"),

        # Graphs Side by Side
        html.Div([
            html.Div("ANALYSIS", className="section-heading"),
            dbc.Row([
                # Spectrograms
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Div("Original Spectrogram", className="graph-title"),
                            html.Span("IN", className="graph-badge"),
                        ], className="graph-header"),
                        dcc.Graph(id='spectrogram-pre', config={'displayModeBar': False},
                                  style={'height': '400px', 'backgroundColor': '#12172e', 'borderRadius': '8px'})
                    ], className="graph-container")
                ], width=12, md=6, id='spectrogram-pre-col'),

                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Div("Processed Spectrogram", className="graph-title"),
                            html.Span("OUT", className="graph-badge"),
                        ], className="graph-header"),
                        dcc.Graph(id='spectrogram-post', config={'displayModeBar': False},
                                  style={'height': '400px', 'backgroundColor': '#12172e', 'borderRadius': '8px'})
                    ], className="graph-container")
                ], width=12, md=6, id='spectrogram-post-col')
            ], className="g-3 mb-3"),

            # Frequency Domain
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Div("Frequency Domain", className="graph-title"),
                            dbc.ButtonGroup([
                                dbc.Button("Linear", id='scale-linear', size="sm",
                                           color="primary", active=True),
                                dbc.Button("Audiogram", id='scale-audiogram', size="sm",
                                           outline=True, color="primary"),
                            ], size="sm")
                        ], className="graph-header"),
                        dcc.Graph(id='frequency-domain', config={'displayModeBar': False},
                                  style={'height': '300px', 'backgroundColor': '#12172e', 'borderRadius': '8px'})
                    ], className="graph-container")
                ], width=12)
            ])
        ], className="app-card"),

        # Equalizer Sliders
        html.Div([
            html.Div("EQUALIZER", className="section-heading"),
            html.Div(id='sliders-container', className='sliders-row')
        ], className="app-card equalizer-section", id='mode-content-area'),

    ], className='tab-content')


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
            verticalHeight=140,
            marks={0: '0', 1: '1', 2: '2'},
            tooltip={"placement": "right"}
        ),
        html.Div([
            html.I(className=slider_config.get('icon', 'fas fa-sliders-h'))
        ], className='slider-icon'),
        html.Label(slider_config['label'], className='slider-label')
    ], className='slider-container')