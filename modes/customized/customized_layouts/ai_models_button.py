# from dash import html, dcc
# import dash_bootstrap_components as dbc
#
#
# def create_ai_interface(id_prefix="ai"):
#     """
#     Creates the AI Interface with DYNAMIC IDs.
#     prefix: 'musical' or 'human' to avoid ID conflicts.
#     """
#     return html.Div([
#         # 1. Trigger Button
#         dbc.Button(
#             [html.I(className="fas fa-robot me-2"), "Try AI Equalizer"],
#             id=f'{id_prefix}-equalizer-btn',  # e.g. human-ai-equalizer-btn
#             color="info",
#             size="lg",
#             className="w-100 mb-3"
#         ),
#
#         # 2. Status Message
#         html.Div(id=f'{id_prefix}-loading-status', className="text-center text-muted mb-2"),
#
#         # 3. Sliders Container
#         dcc.Loading(
#             id=f"{id_prefix}-loading-separation",
#             type="default",
#             children=html.Div(id=f"{id_prefix}-sliders-container")
#         ),
#
#         html.Hr(),
#
#         # 4. Audio Player
#         html.Div([
#             html.H5("AI Mixed Output:", className="text-center"),
#             html.Audio(
#                 id=f'{id_prefix}-audio-player',
#                 controls=True,
#                 style={'width': '100%'}
#             )
#         ], id=f'{id_prefix}-player-container', style={'display': 'none'}),
#
#         # 5. Hidden Store
#         dcc.Store(id=f'{id_prefix}-stems-store')
#     ])

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_ai_tab_content(id_prefix="ai", is_supported=True):
    """
    Creates the AI mode tab content.

    Args:
        id_prefix (str): Unique identifier prefix.
        is_supported (bool): Flag to determine if AI features should be rendered.
    """

    # --- CHECK SUPPORT FLAG ---
    if not is_supported:
        return html.Div([
            html.Div([
                html.I(className="fas fa-ban",
                       style={'fontSize': '4rem', 'color': '#dc3545', 'marginBottom': '1.5rem'}),
                html.H4("AI Model Not Supported", style={'marginBottom': '1rem'}),
                html.P("The AI processing model is not available for this specific mode.",
                       className="text-secondary", style={'fontSize': '1.1rem'}),
                html.P("Please return to Manual Mode or select a different configuration.",
                       className="text-muted")
            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'justifyContent': 'center',
                'padding': '4rem',
                'height': '100%',
                'minHeight': '400px'
            })
        ], className='app-card tab-content')

    # --- RENDER MAIN CONTENT IF SUPPORTED ---
    return html.Div([
        # AI Control Panel
        html.Div([
            html.Div("AI PROCESSING", className="section-heading"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-robot",
                               style={'fontSize': '3rem', 'color': '#b24bf3', 'marginBottom': '1rem'}),
                        html.H5("AI-Powered Separation", style={'marginBottom': '0.5rem'}),
                        html.P("Let AI automatically separate and isolate audio sources",
                               className="text-secondary", style={'fontSize': '0.9rem'}),
                        dbc.Button([
                            html.I(className="fas fa-magic me-2"),
                            "Start AI Separation"
                        ], id=f'{id_prefix}-equalizer-btn', color="info", size="lg", className="w-100"),
                        html.Div(id=f'{id_prefix}-loading-status', className="text-center mt-3")
                    ], style={'textAlign': 'center', 'padding': '2rem'})
                ], width=12, md=4),

                dbc.Col([
                    html.Div([
                        html.Div("AI SLIDERS", className="section-heading"),
                        dcc.Loading(
                            id=f"{id_prefix}-loading-separation",
                            type="default",
                            children=html.Div(id=f"{id_prefix}-sliders-container", className='sliders-row')
                        ),
                        html.Div([
                            # Original String ID
                            html.Audio(id=f'{id_prefix}-audio-player', controls=True, style={'width': '100%'})
                        ], id=f'{id_prefix}-player-container', style={'display': 'none', 'marginTop': '1rem'})
                    ])
                ], width=12, md=8)
            ])
        ], className="app-card"),

        # AI Analysis Graphs
        html.Div([
            html.Div("AI ANALYSIS", className="section-heading"),
            dbc.Row([
                # AI Spectrogram
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Div("AI Output Spectrogram", className="graph-title"),
                            html.Span("AI", className="graph-badge",
                                      style={'background': 'linear-gradient(135deg, #b24bf3, #4a9eff)'}),
                        ], className="graph-header"),
                        dcc.Graph(id='ai-spectrogram', config={'displayModeBar': False},
                                  style={'height': '400px', 'backgroundColor': '#12172e', 'borderRadius': '8px'})
                    ], className="graph-container")
                ], width=12, md=6),

                # AI Frequency Domain
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.Div("AI Frequency Domain", className="graph-title"),
                            html.Span("AI", className="graph-badge",
                                      style={'background': 'linear-gradient(135deg, #b24bf3, #4a9eff)'}),
                        ], className="graph-header"),
                        dcc.Graph(id='ai-frequency-domain', config={'displayModeBar': False},
                                  style={'height': '400px', 'backgroundColor': '#12172e', 'borderRadius': '8px'})
                    ], className="graph-container")
                ], width=12, md=6)
            ], className="g-3")
        ], className="app-card"),

        # Comparison Section
        html.Div([
            html.Div("COMPARISON: MANUAL vs AI", className="section-heading"),
            html.P("Compare the performance of manual equalization versus AI separation",
                   className="text-secondary", style={'fontSize': '0.9rem', 'marginBottom': '1rem'}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("Manual Mode", className="text-center mb-2",
                                 style={'color': '#00d9ff', 'fontWeight': 'bold'}),
                        html.Div("Uses frequency band filtering",
                                 className="text-center text-secondary", style={'fontSize': '0.8rem'})
                    ], className="comparison-panel manual")
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.Div("AI Mode", className="text-center mb-2",
                                 style={'color': '#b24bf3', 'fontWeight': 'bold'}),
                        html.Div("Uses deep learning source separation",
                                 className="text-center text-secondary", style={'fontSize': '0.8rem'})
                    ], className="comparison-panel ai")
                ], width=6)
            ])
        ], className="app-card"),

        # Hidden stores for AI
        dcc.Store(id=f'{id_prefix}-stems-store'),
        dcc.Store(id=f'{id_prefix}-processed-signal-store')

    ], className='tab-content')


