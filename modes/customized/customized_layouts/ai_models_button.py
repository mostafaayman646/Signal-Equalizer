# from dash import html, dcc
# import dash_bootstrap_components as dbc
#
#
# def create_ai_interface():
#     """
#     Creates the complete AI Interface:
#     1. The Trigger Button
#     2. A Status Message area
#     3. A Loading Spinner wrapping the Sliders container
#     4. NEW: A Dedicated Audio Player for AI Output
#     5. Invisible Stores
#     """
#     return html.Div([
#         # 1. The Trigger Button
#         dbc.Button(
#             [html.I(className="fas fa-robot me-2"), "Try AI Equalizer"],
#             id='ai-equalizer-btn',
#             color="info",
#             size="lg",
#             className="w-100 mb-3"
#         ),
#
#         # 2. Status Message
#         html.Div(id='loading-status', className="text-center text-muted mb-2"),
#
#         # 3. Loading Spinner & Sliders Container
#         dcc.Loading(
#             id="loading-separation",
#             type="default",
#             children=html.Div(id="ai-sliders-container")
#         ),
#
#         html.Hr(),
#
#         # 4. NEW: Dedicated AI Audio Player
#         # Initially hidden, appears when sliders are generated
#         html.Div([
#             html.H5("AI Mixed Output:", className="text-center"),
#             html.Audio(
#                 id='ai-audio-player',  # <--- UNIQUE ID
#                 controls=True,
#                 style={'width': '100%'}
#             )
#         ], id='ai-player-container', style={'display': 'none'}),  # Hidden by default
#
#         # 5. Hidden Stores
#         dcc.Store(id='ai-stems-store')
#     ])

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_ai_interface(id_prefix="ai"):
    """
    Creates the AI Interface with DYNAMIC IDs.
    prefix: 'musical' or 'human' to avoid ID conflicts.
    """
    return html.Div([
        # 1. Trigger Button
        dbc.Button(
            [html.I(className="fas fa-robot me-2"), "Try AI Equalizer"],
            id=f'{id_prefix}-equalizer-btn',  # e.g. human-ai-equalizer-btn
            color="info",
            size="lg",
            className="w-100 mb-3"
        ),

        # 2. Status Message
        html.Div(id=f'{id_prefix}-loading-status', className="text-center text-muted mb-2"),

        # 3. Sliders Container
        dcc.Loading(
            id=f"{id_prefix}-loading-separation",
            type="default",
            children=html.Div(id=f"{id_prefix}-sliders-container")
        ),

        html.Hr(),

        # 4. Audio Player
        html.Div([
            html.H5("AI Mixed Output:", className="text-center"),
            html.Audio(
                id=f'{id_prefix}-audio-player',
                controls=True,
                style={'width': '100%'}
            )
        ], id=f'{id_prefix}-player-container', style={'display': 'none'}),

        # 5. Hidden Store
        dcc.Store(id=f'{id_prefix}-stems-store')
    ])