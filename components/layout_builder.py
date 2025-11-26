# """
# Layout Builder - Tab-Based Design with Manual vs AI Modes
# Compact, modern layout with synchronized controls
# """
#
# from dash import html, dcc
# import dash_bootstrap_components as dbc
#
# from Utils.cine_viewers import CineViewer
#
# cine_viewer = CineViewer(namespace="cine")
#
#
# def create_app_layout():
#     """Creates the main application layout with tabs"""
#
#     return html.Div([
#         # Stores
#         dcc.Store(id='current-mode', data='Musical_Instruments'),
#         dcc.Store(id='signal-data-store'),
#         dcc.Store(id='frequency-domain-data'),
#         dcc.Store(id='processed-signal-store'),
#         dcc.Store(id='generic-subdivisions', data=[]),
#         dcc.Store(id='active-tab', data='manual'),
#         dcc.Store(id='slider-sync-store'),
#
#         # Navigation Bar
#         create_navbar(),
#
#         # Main Content Container
#         dbc.Container(fluid=True, className="main-app-content", children=[
#             # Control Deck (Always Visible)
#             create_control_deck(),
#
#             # Tab Selector
#             create_tab_selector(),
#
#             # Tab Content Container
#             html.Div([
#                 # Manual Tab (Initially Visible)
#                 html.Div(create_manual_tab_content(), id='manual-tab-wrapper', style={'display': 'block'}),
#                 # AI Tab (Initially Hidden)
#                 html.Div(id='ai-tab-wrapper', style={'display': 'none'}),
#             ], id='tab-content-container')
#         ]),
#
#     ], style={'backgroundColor': '#0a0e27', 'minHeight': '100vh'})
#
#
# def create_navbar():
#     """Creates the navigation bar"""
#     return dbc.Navbar([
#         dbc.Container([
#             dbc.NavbarBrand([
#                 html.I(className="fas fa-waveform-lines me-2"),
#                 "SIGNAL EQUALIZER ",
#                 html.Span("PRO", className='brand-pro')
#             ]),
#
#             dbc.Nav([
#                 dcc.Dropdown(
#                     id='mode-selector',
#                     options=[
#                         {'label': '🎸 Musical Instruments', 'value': 'Musical_Instruments'},
#                         {'label': '🐾 Animal Sounds', 'value': 'Animal_Sounds'},
#                         {'label': '🗣️ Human Voices', 'value': 'Human_Voices'},
#                         {'label': '⚙️ Generic Mode', 'value': 'generic'},
#                     ],
#                     value='Musical_Instruments',
#                     clearable=False,
#                     style={'width': '250px', 'color': '#000'}
#                 )
#             ], className="ms-auto")
#         ], fluid=True)
#     ], className="navbar", dark=True)
#
#
# def create_tab_selector():
#     """Creates the tab selector pills"""
#     return html.Div([
#         html.Button([
#             html.I(className="fas fa-sliders me-2"),
#             "Manual Mode"
#         ], id='tab-manual', className='mode-tab active'),
#
#         html.Button([
#             html.I(className="fas fa-robot me-2"),
#             "AI Mode"
#         ], id='tab-ai', className='mode-tab'),
#     ], className='mode-tabs')
#
#
# def create_control_deck():
#     """Creates the compact control deck"""
#
#     return html.Div([
#         dbc.Row([
#             # Column 1: Upload
#             dbc.Col([
#                 html.Div([
#                     html.I(className="fas fa-cloud-upload-alt",
#                            style={'fontSize': '2rem', 'color': '#00d9ff', 'marginBottom': '0.5rem'}),
#                     html.Div("UPLOAD SIGNAL", className="section-heading",
#                              style={'paddingLeft': 0, 'marginBottom': '0.5rem'}),
#                     dcc.Upload(
#                         id='upload-signal',
#                         children=html.Div([
#                             html.Div("Drag & Drop", style={'fontWeight': 'bold', 'fontSize': '0.95rem'}),
#                             html.Div("or click to select", style={'fontSize': '0.75rem', 'opacity': 0.7})
#                         ]),
#                         className="upload-box",
#                         style={'padding': '1.5rem'}
#                     )
#                 ], className='control-section')
#             ], width=12, lg=4, className="mb-3"),
#
#             # Column 2: Playback Controls
#             dbc.Col([
#                 html.Div([
#                     html.I(className="fas fa-headphones",
#                            style={'fontSize': '2rem', 'color': '#00d9ff', 'marginBottom': '0.5rem'}),
#                     html.Div("PLAYBACK", className="section-heading",
#                              style={'paddingLeft': 0, 'marginBottom': '0.5rem'}),
#                     dbc.ButtonGroup([
#                         dbc.Button([html.I(className="fas fa-play me-1"), "Original"],
#                                    id='load-before', color="primary", size="sm"),
#                         dbc.Button([html.I(className="fas fa-waveform-lines me-1"), "Processed"],
#                                    id='load-after', color="success", size="sm"),
#                     ], className="w-100 mb-2"),
#                     dbc.Row([
#                         dbc.Col([
#                             html.Audio(id='audio-player-before', controls=True,
#                                        style={'width': '100%', 'height': '35px'})
#                         ], width=6),
#                         dbc.Col([
#                             html.Audio(id='audio-player-after', controls=True,
#                                        style={'width': '100%', 'height': '35px'})
#                         ], width=6),
#                     ])
#                 ], className='control-section')
#             ], width=12, lg=4, className="mb-3"),
#
#             # Column 3: Display & Export
#             dbc.Col([
#                 html.Div([
#                     html.I(className="fas fa-cog",
#                            style={'fontSize': '2rem', 'color': '#00d9ff', 'marginBottom': '0.5rem'}),
#                     html.Div("OPTIONS", className="section-heading",
#                              style={'paddingLeft': 0, 'marginBottom': '0.5rem'}),
#                     dbc.Checklist(
#                         id='spectrogram-toggle',
#                         options=[{'label': ' Show Spectrograms', 'value': 'show'}],
#                         value=['show'],
#                         switch=True,
#                         className="mb-2"
#                     ),
#                     dbc.Button([html.I(className="fas fa-download me-2"), "Export"],
#                                id='download-audio-btn', color="info", size="sm", className="w-100"),
#                     dcc.Download(id="download-processed-audio"),
#                 ], className='control-section')
#             ], width=12, lg=4, className="mb-3"),
#         ])
#     ], className="app-card")
#
#
# def create_manual_tab_content():
#     """Creates the manual mode tab content"""
#
#     return html.Div([
#         # Cine Viewer (Time Domain)
#         html.Div(cine_viewer.layout(), className="app-card"),
#
#         # Graphs Side by Side
#         html.Div([
#             html.Div("ANALYSIS", className="section-heading"),
#             dbc.Row([
#                 # Spectrograms
#                 dbc.Col([
#                     html.Div([
#                         html.Div([
#                             html.Div("Original Spectrogram", className="graph-title"),
#                             html.Span("IN", className="graph-badge"),
#                         ], className="graph-header"),
#                         dcc.Graph(id='spectrogram-pre', config={'displayModeBar': False},
#                                   style={'height': '400px', 'backgroundColor': '#12172e', 'borderRadius': '8px'})
#                     ], className="graph-container")
#                 ], width=12, md=6, id='spectrogram-pre-col'),
#
#                 dbc.Col([
#                     html.Div([
#                         html.Div([
#                             html.Div("Processed Spectrogram", className="graph-title"),
#                             html.Span("OUT", className="graph-badge"),
#                         ], className="graph-header"),
#                         dcc.Graph(id='spectrogram-post', config={'displayModeBar': False},
#                                   style={'height': '400px', 'backgroundColor': '#12172e', 'borderRadius': '8px'})
#                     ], className="graph-container")
#                 ], width=12, md=6, id='spectrogram-post-col')
#             ], className="g-3 mb-3"),
#
#             # Frequency Domain
#             dbc.Row([
#                 dbc.Col([
#                     html.Div([
#                         html.Div([
#                             html.Div("Frequency Domain", className="graph-title"),
#                             dbc.ButtonGroup([
#                                 dbc.Button("Linear", id='scale-linear', size="sm",
#                                            color="primary", active=True),
#                                 dbc.Button("Audiogram", id='scale-audiogram', size="sm",
#                                            outline=True, color="primary"),
#                             ], size="sm")
#                         ], className="graph-header"),
#                         dcc.Graph(id='frequency-domain', config={'displayModeBar': False},
#                                   style={'height': '300px', 'backgroundColor': '#12172e', 'borderRadius': '8px'})
#                     ], className="graph-container")
#                 ], width=12)
#             ])
#         ], className="app-card"),
#
#         # Equalizer Sliders
#         html.Div([
#             html.Div("EQUALIZER", className="section-heading"),
#             html.Div(id='sliders-container', className='sliders-row')
#         ], className="app-card equalizer-section", id='mode-content-area'),
#
#     ], className='tab-content')
#
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
#             verticalHeight=140,
#             marks={0: '0', 1: '1', 2: '2'},
#             tooltip={"placement": "right"}
#         ),
#         html.Div([
#             html.I(className=slider_config.get('icon', 'fas fa-sliders-h'))
#         ], className='slider-icon'),
#         html.Label(slider_config['label'], className='slider-label')
#     ], className='slider-container')

"""
Layout Builder - Compact Professional Design
Optimized for minimal vertical space
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

from Utils.cine_viewers import CineViewer

cine_viewer = CineViewer(namespace="cine")


def create_app_layout():
    """Creates the compact application layout"""

    return html.Div([
        # Stores
        dcc.Store(id='current-mode', data='Musical_Instruments'),
        dcc.Store(id='signal-data-store'),
        dcc.Store(id='frequency-domain-data'),
        dcc.Store(id='processed-signal-store'),
        dcc.Store(id='generic-subdivisions', data=[]),
        dcc.Store(id='active-tab', data='manual'),
        dcc.Store(id='slider-sync-store'),
        dcc.Store(id='control-deck-visible', data=False),

        # Compact Navigation Bar
        create_navbar(),

        # Main Content Container - Compact
        dbc.Container(fluid=True, className="main-app-content", children=[
            # Collapsible Control Deck
            create_collapsible_control_deck(),

            # Tab Selector
            create_tab_selector(),

            # Tab Content Container
            html.Div([
                # Manual Tab (Initially Visible)
                html.Div(create_compact_manual_tab(), id='manual-tab-wrapper', style={'display': 'block'}),
                # AI Tab (Initially Hidden)
                html.Div(id='ai-tab-wrapper', style={'display': 'none'}),
            ], id='tab-content-container')
        ]),

    ], style={'backgroundColor': '#0a0e27', 'minHeight': '100vh'})


def create_navbar():
    """Creates compact navigation bar"""
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
                    style={'width': '220px', 'color': '#000'}
                )
            ], className="ms-auto")
        ], fluid=True)
    ], className="navbar", dark=True)


def create_tab_selector():
    """Creates compact tab selector"""
    return html.Div([
        html.Button([
            html.I(className="fas fa-sliders me-2"),
            "Manual"
        ], id='tab-manual', className='mode-tab active'),

        html.Button([
            html.I(className="fas fa-robot me-2"),
            "AI"
        ], id='tab-ai', className='mode-tab'),
    ], className='mode-tabs')


def create_collapsible_control_deck():
    """Creates collapsible control deck to save space"""

    return html.Div([
        # Toggle Button
        html.Div([
            html.Div([
                html.I(className="fas fa-sliders-h me-2"),
                html.Span("CONTROLS", style={'fontWeight': '600', 'fontSize': '0.85rem'})
            ]),
            html.I(id='control-deck-icon', className="fas fa-chevron-down")
        ], id='control-deck-toggle', className='control-deck-toggle'),

        # Collapsible Content
        html.Div([
            html.Div([
                dbc.Row([
                    # Upload
                    dbc.Col([
                        html.Div([
                            html.Div("UPLOAD", className="section-heading-compact"),
                            dcc.Upload(
                                id='upload-signal',
                                children=html.Div([
                                    html.I(className="fas fa-cloud-upload-alt me-1"),
                                    "Select File"
                                ]),
                                className="upload-box"
                            )
                        ], className='control-section')
                    ], width=12, md=4, className="mb-2"),

                    # Playback
                    dbc.Col([
                        html.Div([
                            html.Div("PLAYBACK", className="section-heading-compact"),
                            dbc.ButtonGroup([
                                dbc.Button([html.I(className="fas fa-play")],
                                          id='load-before', color="primary", size="sm"),
                                dbc.Button([html.I(className="fas fa-waveform-lines")],
                                          id='load-after', color="success", size="sm"),
                            ], size="sm", className="w-100 mb-1"),
                            dbc.Row([
                                dbc.Col(html.Audio(id='audio-player-before', controls=True,
                                                  style={'width': '100%', 'height': '30px'}), width=6),
                                dbc.Col(html.Audio(id='audio-player-after', controls=True,
                                                  style={'width': '100%', 'height': '30px'}), width=6),
                            ], className="g-1")
                        ], className='control-section')
                    ], width=12, md=5, className="mb-2"),

                    # Options
                    dbc.Col([
                        html.Div([
                            html.Div("OPTIONS", className="section-heading-compact"),
                            dbc.Checklist(
                                id='spectrogram-toggle',
                                options=[{'label': ' Spectrograms', 'value': 'show'}],
                                value=['show'],
                                switch=True,
                                className="mb-1",
                                style={'fontSize': '0.75rem'}
                            ),
                            dbc.Button([html.I(className="fas fa-download me-1"), "Export"],
                                      id='download-audio-btn', color="info", size="sm", className="w-100"),
                            dcc.Download(id="download-processed-audio"),
                        ], className='control-section')
                    ], width=12, md=3, className="mb-2"),
                ])
            ], className="app-card")
        ], id='control-deck-container', className='control-deck-container hidden')
    ])


def create_compact_manual_tab():
    """Creates compact manual mode tab - new layout"""

    return html.Div([
        # Row 1: Sliders Left + Frequency Right (Side by Side)
        html.Div([
            # Left Column: Sliders
            html.Div([
                html.Div("EQUALIZER", className="section-heading-compact"),
                html.Div(id='sliders-container', className='sliders-row')
            ], className="sliders-column", id='mode-content-area'),

            # Right Column: Frequency Domain
            html.Div([
                html.Div([
                    html.Div("FREQUENCY DOMAIN", className="section-heading-compact"),
                    dbc.ButtonGroup([
                        dbc.Button("Linear", id='scale-linear', size="sm",
                                  color="primary", active=True),
                        dbc.Button("Audiogram", id='scale-audiogram', size="sm",
                                  outline=True, color="primary"),
                    ], size="sm", className="ms-auto")
                ], style={'display': 'flex', 'justifyContent': 'space-between',
                         'alignItems': 'center', 'marginBottom': '0.25rem'}),
                dcc.Graph(id='frequency-domain', config={'displayModeBar': False},
                         className='frequency-graph-compact')
            ], className="frequency-column")
        ], className="main-equalizer-row"),

        # Row 2: Time Domain Graphs (Side by Side)
        # html.Div([
        #     # Original Signal
        #     html.Div([
        #         html.Div([
        #             html.Div("ORIGINAL SIGNAL", className="graph-title-compact"),
        #             html.Span("IN", className="graph-badge-compact"),
        #         ], className="time-graph-header"),
        #         dcc.Graph(id='cine-graph-pre', config={'displayModeBar': False},
        #                  className='time-graph-compact')
        #     ], className="time-graph-container"),

        #     # Processed Signal
        #     html.Div([
        #         html.Div([
        #             html.Div("PROCESSED SIGNAL", className="graph-title-compact"),
        #             html.Span("OUT", className="graph-badge-compact"),
        #         ], className="time-graph-header"),
        #         dcc.Graph(id='cine-graph-post', config={'displayModeBar': False},
        #                  className='time-graph-compact')
        #     ], className="time-graph-container"),
        # ], className="time-domain-compact"),

        # # Compact Cine Controls
        # html.Div([
        #     dbc.ButtonGroup([
        #         dbc.Button(html.I(className="fas fa-play"), id='cine-play',
        #                   color="primary", size="sm"),
        #         dbc.Button(html.I(className="fas fa-pause"), id='cine-pause',
        #                   color="primary", size="sm"),
        #         dbc.Button(html.I(className="fas fa-stop"), id='cine-stop',
        #                   color="primary", size="sm"),
        #         dbc.Button(html.I(className="fas fa-redo"), id='cine-loop',
        #                   color="secondary", size="sm"),
        #     ], size="sm"),
        #     html.Div([
        #         html.Span("Speed", style={'fontSize': '0.7rem', 'marginRight': '0.5rem'}),
        #         dcc.Slider(
        #             id='cine-speed',
        #             min=0.25, max=2.0, step=0.25, value=1.0,
        #             marks={0.25: '0.25x', 1: '1x', 2: '2x'},
        #             tooltip={"placement": "bottom"},
        #             className="flex-grow-1"
        #         )
        #     ], style={'display': 'flex', 'alignItems': 'center', 'flex': '1', 'marginLeft': '1rem'})
        # ], className="cine-controls-compact"),


                # Row 2: Time Domain Graphs (Side by Side) with Enhanced Controls
        html.Div([
            # Original Signal
            html.Div([
                html.Div([
                    html.Div("ORIGINAL SIGNAL", className="graph-title-compact"),
                    html.Span("IN", className="graph-badge-compact"),
                ], className="time-graph-header"),
                dcc.Graph(
                    id='cine-graph-pre',
                    config={'displayModeBar': False},
                    className='time-graph-compact'
                )
            ], className="time-graph-container"),

            # Processed Signal
            html.Div([
                html.Div([
                    html.Div("PROCESSED SIGNAL", className="graph-title-compact"),
                    html.Span("OUT", className="graph-badge-compact"),
                ], className="time-graph-header"),
                dcc.Graph(
                    id='cine-graph-post',
                    config={'displayModeBar': False},
                    className='time-graph-compact'
                )
            ], className="time-graph-container"),
        ], className="time-domain-compact"),

        # Enhanced Cine Controls with Audio Source Selection
        html.Div([
            # Left side: Playback controls
            html.Div([
                dbc.ButtonGroup([
                    dbc.Button(
                        html.I(className="fas fa-play"),
                        id='cine-play',
                        color="primary",
                        size="sm",
                        title="Play"
                    ),
                    dbc.Button(
                        html.I(className="fas fa-pause"),
                        id='cine-pause',
                        color="primary",
                        size="sm",
                        title="Pause"
                    ),
                    dbc.Button(
                        html.I(className="fas fa-stop"),
                        id='cine-stop',
                        color="primary",
                        size="sm",
                        title="Stop"
                    ),
                    dbc.Button(
                        html.I(className="fas fa-redo"),
                        id='cine-loop',
                        color="secondary",
                        size="sm",
                        title="Toggle Loop"
                    ),
                ], size="sm"),

                # Time display
                html.Div(
                    id='cine-current-time',
                    children="00:00 / 00:00",
                    style={
                        'fontSize': '0.75rem',
                        'fontWeight': '600',
                        'color': 'var(--accent-cyan)',
                        'marginLeft': '1rem',
                        'fontFamily': 'monospace'
                    }
                ),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '0.5rem'}),

            # Middle: Speed control
            html.Div([
                html.Span("Speed", style={
                    'fontSize': '0.7rem',
                    'marginRight': '0.5rem',
                    'color': 'var(--text-secondary)'
                }),
                dcc.Slider(
                    id='cine-speed',
                    min=0.25,
                    max=2.0,
                    step=0.25,
                    value=1.0,
                    marks={0.25: '0.25x', 0.5: '0.5x', 1: '1x', 1.5: '1.5x', 2: '2x'},
                    tooltip={"placement": "bottom"},
                    className="flex-grow-1"
                )
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'flex': '1',
                'marginLeft': '1rem',
                'marginRight': '1rem'
            }),

            # Right side: Audio source selection
            html.Div([
                html.Span("Listen to:", style={
                    'fontSize': '0.75rem',
                    'marginRight': '0.5rem',
                    'color': 'var(--text-primary)',
                    'fontWeight': '600'
                }),
                dbc.RadioItems(
                    id='cine-audio-source-toggle',
                    options=[
                        {'label': ' Original', 'value': 'before'},
                        {'label': ' Processed', 'value': 'after'}
                    ],
                    value='before',
                    inline=True,
                    style={'fontSize': '0.75rem'},
                    className='cine-audio-toggle'
                ),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '0.5rem'}),

        ], className="cine-controls-compact", style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'gap': '1rem',
            'flexWrap': 'wrap'
        }),

        # Audio player with track indicator
        html.Div([
            html.Div([
                html.I(className="fas fa-volume-up me-2", style={'color': 'var(--accent-cyan)'}),
                html.Span("Playing: ", style={'fontSize': '0.7rem', 'color': 'var(--text-secondary)'}),
                html.Span(id='cine-audio-track-label', children="Original",
                          style={'fontSize': '0.75rem', 'color': 'var(--accent-cyan)', 'fontWeight': '600'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0.25rem'}),
            html.Audio(
                id='cine-audio-player',
                controls=True,
                autoPlay=False,
                style={
                    'width': '100%',
                    'height': '35px',
                    'backgroundColor': 'var(--secondary-bg)',
                    'borderRadius': '6px'
                }
            ),
        ], style={'marginTop': '0.5rem'}),

        # Hidden stores for cine viewer
        dcc.Store(id='cine-window-state'),
        dcc.Store(id='cine-playback-state'),
        dcc.Interval(id='cine-ticker', interval=100, disabled=True),  # Updated to 100ms



        # Row 3: Spectrograms (Side by Side) - Toggleable
        # Row 3: Spectrograms (Side by Side) - Toggleable
        html.Div([
            html.Div([
                html.Div([
                    html.Div("ORIGINAL SPECTROGRAM", className="graph-title-compact"),
                    html.Span("IN", className="graph-badge-compact"),
                ], className="time-graph-header"),
                dcc.Graph(
                    id='spectrogram-pre',
                    config={'displayModeBar': False, 'responsive': True},
                    className='spec-graph-compact',
                    style={'width': '100%', 'height': '220px'}
                )
            ], className="spec-container"),

            html.Div([
                html.Div([
                    html.Div("PROCESSED SPECTROGRAM", className="graph-title-compact"),
                    html.Span("OUT", className="graph-badge-compact"),
                ], className="time-graph-header"),
                dcc.Graph(
                    id='spectrogram-post',
                    config={'displayModeBar': False, 'responsive': True},
                    className='spec-graph-compact',
                    style={'width': '100%', 'height': '220px'}
                )
            ], className="spec-container"),
        ], className="spectrogram-row", id='spectrogram-row'),

        # Hidden stores for cine viewer
        # dcc.Store(id='cine-window-state'),
        # dcc.Store(id='cine-playback-state'),
        dcc.Store(id='cine-last-relayout'),
        # dcc.Interval(id='cine-ticker', interval=50, disabled=True),

    ], className='tab-content')


def create_slider(slider_config):
    """Creates a VERTICAL slider with icon BELOW"""

    return html.Div([
        # Slider FIRST (order: 1 by default)
        html.Div([
            dcc.Slider(
                id={'type': 'equalizer-slider', 'index': slider_config['id']},
                min=0,
                max=2,
                step=0.1,
                value=slider_config.get('gain', 1.0),
                marks={0: '0', 1: '1', 2: '2'},
                tooltip={"placement": "right", "always_visible": False},
                vertical=True,
                verticalHeight=140,
                updatemode='drag'
            )
        ], className='equalizer-slider'),
        
        # Icon SECOND (order: 2 from CSS)
        html.Div([
            html.I(className=slider_config.get('icon', 'fas fa-sliders-h'))
        ], className='slider-icon'),
        
        # Label THIRD (order: 3 from CSS)
        html.Label(slider_config['label'], className='slider-label'),
        
    ], className='slider-container')