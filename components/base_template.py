
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_sidebar(mode_name="Music and Animals", show_spectrogram=True):
    """
    Creates the left sidebar with sound source selection and controls.

    Args:
        mode_name: Current mode name to display
        show_spectrogram: Whether to show spectrogram toggle

    Returns:
        dbc.Col: Sidebar column component
    """
    return dbc.Col([
        # Sound Source Section
        html.Div([
            html.H6("SOUND SOURCE", className="sidebar-heading"),
            dcc.Dropdown(
                id='mode-selector',
                options=[
                    {'label': 'Generic Mode', 'value': 'generic'},
                    {'label': 'Music and Animals', 'value': 'music_animals'},
                    {'label': 'Musical Instruments', 'value': 'instruments'},
                    {'label': 'Animal Sounds', 'value': 'animals'},
                    {'label': 'Human Voices', 'value': 'voices'}
                ],
                value='music_animals',
                className="mode-dropdown"
            ),
        ], className="sidebar-section"),

        # Upload Section
        html.Div([
            dcc.Upload(
                id='upload-signal',
                children=html.Div([
                    html.I(className="fas fa-upload"),
                    html.Span(" Upload Signal")
                ]),
                className="upload-box",
                multiple=False
            ),
        ], className="sidebar-section"),

        # Spectrogram Toggle (optional)
        html.Div([
            html.Label("Spectrograms Display", className="sidebar-label"),
            dbc.Checklist(
                id='spectrogram-toggle',
                options=[{'label': ' Show Spectrograms', 'value': 'show'}],
                value=['show'] if show_spectrogram else [],
                switch=True,
                className="spectrogram-switch"
            ),
        ], className="sidebar-section", id='spectrogram-toggle-section'),

        # Equalizer Icon
        html.Div([
            html.Div([
                html.I(className="fas fa-sliders-h fa-3x",
                       style={'color': '#00d9ff'})
            ], className="equalizer-icon-container"),
            html.H6("SOUND SOURCE", className="sidebar-subheading"),
            html.H6("EFFECTS", className="sidebar-subheading mt-3"),
        ], className="sidebar-section text-center"),

        # Audio Playback Controls
        html.Div([
            html.Label("Sound Before:", className="audio-label"),
            html.Button([
                html.I(className="fas fa-volume-up")
            ], id='play-before', className="audio-button"),

            html.Label("Sound After:", className="audio-label mt-2"),
            html.Button([
                html.I(className="fas fa-volume-up")
            ], id='play-after', className="audio-button"),
        ], className="sidebar-section"),

        # Settings Save/Load Section
        html.Div([
            html.Button([
                html.I(className="fas fa-save"),
                " Save Settings"
            ], id='save-settings-btn', className="settings-button"),

            html.Button([
                html.I(className="fas fa-folder-open"),
                " Load Settings"
            ], id='load-settings-btn', className="settings-button mt-2"),

            dcc.Download(id="download-settings"),
            dcc.Upload(
                id='upload-settings',
                children=html.Div([]),
                style={'display': 'none'}
            ),
        ], className="sidebar-section"),

    ], width=2, className="sidebar", id='sidebar')


def create_time_domain_viewers():
    """
    Creates the two synchronized time domain viewers (Pre and Post signal).

    Returns:
        html.Div: Container with both time domain graphs
    """
    return html.Div([
        html.H5("TIME DOMAIN", className="section-heading"),

        # Pre-Signal Graph
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='time-domain-pre',
                    config={'displayModeBar': False},
                    className="signal-graph"
                )
            ], width=10),
            dbc.Col([
                dcc.Graph(
                    id='spectrogram-pre',
                    config={'displayModeBar': False},
                    className="spectrogram-mini"
                )
            ], width=2, id='spectrogram-pre-col')
        ], className="graph-row"),

        # Post-Signal Graph
        html.H5("TIME DOMAIN", className="section-heading mt-3"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='time-domain-post',
                    config={'displayModeBar': False},
                    className="signal-graph"
                )
            ], width=10),
            dbc.Col([
                dcc.Graph(
                    id='spectrogram-post',
                    config={'displayModeBar': False},
                    className="spectrogram-mini"
                )
            ], width=2, id='spectrogram-post-col')
        ], className="graph-row"),

    ], className="time-domain-section")


def create_playback_controls():
    """
    Creates the global playback controls (play, pause, zoom, etc.).

    Returns:
        html.Div: Playback controls toolbar
    """
    return html.Div([
        dbc.ButtonGroup([
            # Global Controls Dropdown
            dbc.DropdownMenu(
                label="GLOBAL CONTROLS",
                children=[
                    dbc.DropdownMenuItem("Reset All", id='reset-all'),
                    dbc.DropdownMenuItem("Reset View", id='reset-view'),
                    dbc.DropdownMenuItem("Reset Sliders", id='reset-sliders'),
                ],
                className="global-controls-dropdown"
            ),

            # Zoom Controls
            dbc.Button(html.I(className="fas fa-plus"), id='zoom-in',
                       outline=True, color="secondary", size="sm"),
            dbc.Button(html.I(className="fas fa-minus"), id='zoom-out',
                       outline=True, color="secondary", size="sm"),

            # Playback Controls
            dbc.Button(html.I(className="fas fa-play"), id='play-btn',
                       outline=True, color="primary", size="sm"),
            dbc.Button(html.I(className="fas fa-pause"), id='pause-btn',
                       outline=True, color="primary", size="sm"),
            dbc.Button(html.I(className="fas fa-stop"), id='stop-btn',
                       outline=True, color="primary", size="sm"),

            # Additional Controls
            dbc.Button(html.I(className="fas fa-plus-circle"), id='add-marker',
                       outline=True, color="secondary", size="sm"),
            dbc.Button(html.I(className="fas fa-forward"), id='skip-forward',
                       outline=True, color="secondary", size="sm"),
            dbc.Button(html.I(className="fas fa-redo"), id='loop-btn',
                       outline=True, color="secondary", size="sm"),

            # Zoom to Fit
            dbc.Button([
                html.I(className="fas fa-expand"),
                " Zoom to fit"
            ], id='zoom-fit', outline=True, color="secondary", size="sm"),

        ], className="playback-controls"),

        # Speed Control Slider
        html.Div([
            html.Label("Playback Speed:", className="speed-label"),
            dcc.Slider(
                id='playback-speed',
                min=0.25,
                max=2.0,
                step=0.25,
                value=1.0,
                marks={0.25: '0.25x', 0.5: '0.5x', 1.0: '1x',
                       1.5: '1.5x', 2.0: '2x'},
                className="speed-slider"
            )
        ], className="speed-control mt-2")

    ], className="controls-section my-3")


def create_frequency_domain_viewer():
    """
    Creates the frequency domain visualization with scale selector.

    Returns:
        html.Div: Frequency domain graph and controls
    """
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H5("FREQUENCY DOMAIN", className="section-heading")
            ], width=9),
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("Linear", id='scale-linear',
                               color="primary", size="sm", active=True),
                    dbc.Button("Audiogram", id='scale-audiogram',
                               color="primary", size="sm", outline=True),
                ], className="scale-selector")
            ], width=3, className="text-end")
        ]),

        dcc.Graph(
            id='frequency-domain',
            config={'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d']},
            className="frequency-graph"
        )

    ], className="frequency-domain-section mt-3")


def create_equalizer_sliders(slider_configs):
    """
    Creates the equalizer slider section with custom icons/labels.

    Args:
        slider_configs: List of dicts with keys:
            - id: unique slider id
            - label: slider label text
            - icon: icon class or image path
            - min: minimum value (default 0)
            - max: maximum value (default 2)
            - value: initial value (default 1)
            - step: step size (default 0.1)

    Returns:
        html.Div: Equalizer sliders container
    """
    sliders = []

    for config in slider_configs:
        slider_id = config.get('id')
        label = config.get('label', 'Slider')
        icon = config.get('icon', 'fas fa-music')
        min_val = config.get('min', 0)
        max_val = config.get('max', 2)
        value = config.get('value', 1)
        step = config.get('step', 0.1)

        slider_component = html.Div([
            # Slider
            dcc.Slider(
                id=slider_id,
                min=min_val,
                max=max_val,
                step=step,
                value=value,
                vertical=True,
                verticalHeight=150,
                marks={min_val: str(min_val), max_val: str(max_val)},
                className="equalizer-slider",
                tooltip={"placement": "right", "always_visible": False}
            ),

            # Icon/Image
            html.Div([
                html.I(className=icon) if icon.startswith('fa')
                else html.Img(src=icon, className="slider-icon-img")
            ], className="slider-icon"),

            # Label
            html.Label(label, className="slider-label")

        ], className="slider-container")

        sliders.append(slider_component)

    return html.Div([
        html.H5("FREQUENCY DOMAIN", className="section-heading"),
        html.Div(
            sliders,
            className="sliders-row"
        )
    ], className="equalizer-section mt-3")


def create_base_layout(slider_configs, mode_name="Music and Animals",
                       additional_components=None):
    """
    Creates the complete base layout combining all components.
    This is the main function each mode will call.

    Args:
        slider_configs: Configuration for equalizer sliders
        mode_name: Name of current mode
        additional_components: Optional list of additional Dash components
                              to add after sliders

    Returns:
        html.Div: Complete application layout
    """
    layout = html.Div([
        # Top Navigation Bar
        # dbc.Navbar([
        #     dbc.Container([
        #         dbc.NavbarBrand([
        #             html.I(className="fas fa-cloud-upload-alt me-2"),
        #             "SIGNAL EQUALIZER ",
        #             html.Span("PRO", className="brand-pro")
        #         ], className="navbar-brand"),
        #
        #         # Hamburger menu for mobile
        #         dbc.NavbarToggler(id="navbar-toggler"),
        #
        #     ], fluid=True)
        # ], color="dark", dark=True, className="mb-3"),

        # Main Content
        dbc.Container([
            dbc.Row([
                # Sidebar
                create_sidebar(mode_name),

                # Main Content Area
                dbc.Col([
                    # Time Domain Viewers
                    create_time_domain_viewers(),

                    # Playback Controls
                    create_playback_controls(),

                    # Frequency Domain Viewer
                    create_frequency_domain_viewer(),

                    # Equalizer Sliders
                    create_equalizer_sliders(slider_configs),

                    # Additional mode-specific components
                    html.Div(
                        additional_components if additional_components else [],
                        id='additional-components'
                    )

                ], width=10, className="main-content")
            ])
        ], fluid=True, className="main-container"),

        # Hidden Data Stores
        dcc.Store(id='signal-data-store'),  # Stores original signal
        dcc.Store(id='processed-signal-store'),  # Stores processed signal
        dcc.Store(id='playback-state-store'),  # Stores playback state
        dcc.Store(id='slider-states-store'),  # Stores all slider values
        dcc.Interval(id='playback-interval', interval=50, disabled=True),

        # Audio elements (hidden)
        html.Audio(id='audio-player-before', controls=False,
                   style={'display': 'none'}),
        html.Audio(id='audio-player-after', controls=False,
                   style={'display': 'none'}),

    ], className="app-container")

    return layout


def create_generic_mode_additions():
    """
    Additional components specific to Generic Mode.

    Returns:
        list: Additional components for generic mode
    """
    return [
        html.Div([
            html.H5("SUBDIVISION MANAGEMENT", className="section-heading mt-4"),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="fas fa-plus-circle me-2"),
                    "Add Subdivision"
                ], id='add-subdivision', color="success", size="sm"),

                dbc.Button([
                    html.I(className="fas fa-trash me-2"),
                    "Remove Last"
                ], id='remove-subdivision', color="danger",
                    size="sm", outline=True),
            ]),

            html.Div(id='subdivisions-container', className="mt-3")

        ], className="generic-mode-section")
    ]

# Example usage for different modes would be:
#
# # In modes/musical_instruments/layout.py:
# from components.base_template import create_base_layout
#
# slider_configs = [
#     {'id': 'slider-guitar', 'label': 'Guitar', 'icon': 'fas fa-guitar'},
#     {'id': 'slider-piano', 'label': 'Piano', 'icon': 'fas fa-piano'},
#     {'id': 'slider-drums', 'label': 'Drums', 'icon': 'fas fa-drum'},
#     {'id': 'slider-flute', 'label': 'Flute', 'icon': 'fas fa-music'},
# ]
#
# layout = create_base_layout(slider_configs, mode_name="Musical Instruments")