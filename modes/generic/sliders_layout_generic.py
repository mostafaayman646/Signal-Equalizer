# from dash import html, dcc
# import dash_bootstrap_components as dbc
#
# from components.layouts.Create_Sliders_Area import create_sliders_area
#
#
# def create_generic_controls_area():
#     """Creates the sliders area for generic mode with helper UI/state."""
#
#     base_section = create_sliders_area()
#     children = list(base_section.children)
#
#     helper_block = html.Div(
#         [
#             html.Div(
#                 "Click anywhere on the frequency plot to capture the low and high edge "
#                 "of a custom band. We'll open a quick editor so you can fine-tune the "
#                 "numbers before saving the slider.",
#                 className="text-muted",
#                 style={"fontSize": "0.8rem"},
#             ),
#             html.Div(
#                 [
#                     html.Span("Selection status:", className="me-2"),
#                     html.Span(
#                         "Waiting for clicks…",
#                         id="generic-selection-helper",
#                         className="fw-semibold",
#                     ),
#                     dbc.Button(
#                         "Clear selection",
#                         id="generic-clear-selection",
#                         size="sm",
#                         color="secondary",
#                         outline=True,
#                         className="ms-auto",
#                     ),
#                 ],
#                 className="d-flex align-items-center gap-2 flex-wrap mt-2",
#                 style={"fontSize": "0.75rem"},
#             ),
#         ],
#         className="mb-3",
#     )
#
#     json_controls = html.Div(
#         [
#             dbc.ButtonGroup(
#                 [
#                     dbc.Button(
#                         [html.I(className="fas fa-save me-2"), "Save presets"],
#                         id="generic-save-json",
#                         color="success",
#                         size="sm",
#                     ),
#                     dbc.Button(
#                         [html.I(className="fas fa-folder-open me-2"), "Load presets"],
#                         id="generic-load-json",
#                         color="warning",
#                         size="sm",
#                     ),
#                 ],
#                 className="me-3",
#             ),
#             html.Div(
#                 id="generic-json-feedback",
#                 className="text-muted small",
#                 style={"flex": "1 1 auto"},
#             ),
#         ],
#         className="d-flex align-items-center gap-2 flex-wrap mb-3",
#     )
#
#     # Insert helper block right after the heading inside the base equalizer section
#     if len(children) >= 2:
#         children.insert(1, helper_block)
#         children.insert(2, json_controls)
#     else:
#         children.append(helper_block)
#         children.append(json_controls)
#     base_section.children = children
#
#     modal = dbc.Modal(
#         [
#             dbc.ModalHeader("Create Custom Frequency Slider"),
#             dbc.ModalBody(
#                 [
#                     dbc.Row(
#                         [
#                             dbc.Col(
#                                 [
#                                     dbc.Label("Low frequency (Hz)"),
#                                     dbc.Input(
#                                         id="generic-range-start",
#                                         type="number",
#                                         min=0,
#                                         step=1,
#                                     ),
#                                 ],
#                                 md=6,
#                                 className="mb-3",
#                             ),
#                             dbc.Col(
#                                 [
#                                     dbc.Label("High frequency (Hz)"),
#                                     dbc.Input(
#                                         id="generic-range-end",
#                                         type="number",
#                                         min=0,
#                                         step=1,
#                                     ),
#                                 ],
#                                 md=6,
#                                 className="mb-3",
#                             ),
#                         ]
#                     ),
#                     dbc.Label("Optional label"),
#                     dbc.Input(
#                         id="generic-band-label",
#                         type="text",
#                         placeholder="e.g. Resonance band",
#                         className="mb-2",
#                     ),
#                     html.Div(
#                         id="generic-modal-feedback",
#                         className="text-danger small",
#                     ),
#                 ]
#             ),
#             dbc.ModalFooter(
#                 [
#                     dbc.Button(
#                         "Cancel",
#                         id="generic-range-cancel",
#                         color="secondary",
#                         outline=True,
#                         className="me-2",
#                     ),
#                     dbc.Button(
#                         "Add slider",
#                         id="generic-range-confirm",
#                         color="info",
#                     ),
#                 ]
#             ),
#         ],
#         id="generic-range-modal",
#         is_open=False,
#         centered=True,
#         backdrop="static",
#     )
#
#     return html.Div(
#         [
#             dcc.Store(id="generic-sliders-store", data=[]),
#             dcc.Store(id="generic-range-draft", data={"points": []}),
#             base_section,
#             modal,
#         ]
#     )

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_generic_controls_area():
    """Creates the sliders area for generic mode with helper UI/state."""

    return html.Div([
        dcc.Store(id="generic-sliders-store", data=[]),
        dcc.Store(id="generic-range-draft", data={"points": []}),

        html.Div([
            html.Div("EQUALIZER", className="section-heading-compact"),

            # Helper block
            html.Div([
                html.Div(
                    "Click two points on the frequency plot to create a custom band.",
                    className="text-muted",
                    style={"fontSize": "0.75rem", "marginBottom": "0.5rem"}
                ),
                html.Div([
                    html.Span("Status: ", className="me-1", style={"fontSize": "0.7rem"}),
                    html.Span(
                        "Waiting for clicks…",
                        id="generic-selection-helper",
                        className="fw-semibold",
                        style={"fontSize": "0.7rem", "color": "var(--accent-cyan)"}
                    ),
                    dbc.Button(
                        "Clear",
                        id="generic-clear-selection",
                        size="sm",
                        color="secondary",
                        outline=True,
                        className="ms-auto",
                        style={"fontSize": "0.65rem", "padding": "0.2rem 0.5rem"}
                    ),
                ], className="d-flex align-items-center gap-2 mb-2"),
            ], style={"marginBottom": "0.5rem"}),

            # JSON controls
            html.Div([
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className="fas fa-save me-1"), "Save"],
                        id="generic-save-json",
                        color="success",
                        size="sm",
                        style={"fontSize": "0.7rem"}
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-folder-open me-1"), "Load"],
                        id="generic-load-json",
                        color="warning",
                        size="sm",
                        style={"fontSize": "0.7rem"}
                    ),
                ], size="sm"),
                html.Div(
                    id="generic-json-feedback",
                    className="text-muted small",
                    style={"fontSize": "0.65rem", "marginTop": "0.25rem"}
                ),
            ], style={"marginBottom": "0.75rem"}),

            # Sliders container
            html.Div(
                id='sliders-container',
                className='sliders-row',
                style={"minHeight": "150px"}
            )
        ], className="generic-controls-area"),

        # Modal for creating sliders
        dbc.Modal([
            dbc.ModalHeader("Create Custom Frequency Band", style={"fontSize": "0.9rem"}),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Low frequency (Hz)", style={"fontSize": "0.75rem"}),
                        dbc.Input(
                            id="generic-range-start",
                            type="number",
                            min=0,
                            step=1,
                            size="sm"
                        ),
                    ], md=6, className="mb-2"),
                    dbc.Col([
                        dbc.Label("High frequency (Hz)", style={"fontSize": "0.75rem"}),
                        dbc.Input(
                            id="generic-range-end",
                            type="number",
                            min=0,
                            step=1,
                            size="sm"
                        ),
                    ], md=6, className="mb-2"),
                ]),
                dbc.Label("Label (optional)", style={"fontSize": "0.75rem"}),
                dbc.Input(
                    id="generic-band-label",
                    type="text",
                    placeholder="e.g., Resonance band",
                    className="mb-2",
                    size="sm"
                ),
                html.Div(
                    id="generic-modal-feedback",
                    className="text-danger",
                    style={"fontSize": "0.7rem"}
                ),
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "Cancel",
                    id="generic-range-cancel",
                    color="secondary",
                    outline=True,
                    size="sm",
                    className="me-2"
                ),
                dbc.Button(
                    "Add slider",
                    id="generic-range-confirm",
                    color="info",
                    size="sm"
                ),
            ]),
        ], id="generic-range-modal", is_open=False, centered=True, backdrop="static", size="md")
    ])