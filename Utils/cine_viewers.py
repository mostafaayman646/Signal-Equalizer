"""
Utility module that wraps the cine (linked time-domain viewer) UI + logic.
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np
import plotly.graph_objects as go
from dash import dcc, html, ctx, no_update
from dash import Input, Output, State
import dash_bootstrap_components as dbc


@dataclass
class CineViewer:
    """
    Reusable cine viewer (paired time-domain plots + playback controls).

    Usage:
        cine = CineViewer(namespace="cine")
        layout_fragment = cine.layout()
        cine.register_callbacks(app)
    """
    namespace: str = "cine"
    max_points: int = 2_000  # plotting LOD target

    def __post_init__(self):
        self._ns: Callable[[str], str] = lambda suffix: f"{self.namespace}-{suffix}"

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def layout(self) -> html.Div:
        ns = self._ns

        def graph_block(graph_id, title, badge_text, readout_id):
            return dbc.Card(
                [
                    dbc.CardHeader(
                        html.Div(
                            [
                                html.Span(
                                    title,
                                    className="text-uppercase small fw-semibold text-secondary",
                                ),
                                html.Span(
                                    badge_text,
                                    className="viewer-badge",
                                ),
                            ],
                            className="d-flex align-items-center justify-content-between gap-2",
                        ),
                        className="py-2 px-3",
                    ),
                    dbc.CardBody(
                        [
                            dcc.Graph(
                                id=graph_id,
                                config={
                                    "displayModeBar": False,
                                    "scrollZoom": True,
                                },
                                className="signal-graph",
                                style={"height": "280px", "minHeight": "260px"},
                            ),
                            html.Div(
                                html.Div(
                                    id=readout_id,
                                    className="cursor-readout fw-semibold mt-1",
                                ),
                                className="mt-3",
                            ),
                        ],
                        className="pt-3 pb-2 px-3",
                    ),
                ],
                className="cine-graph-card shadow-sm h-100",
            )

        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            "TIME DOMAIN",
                            className="section-heading text-uppercase mb-3",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    graph_block(
                                        ns("graph-pre"),
                                        "Original Signal",
                                        "IN",
                                        ns("cursor-readout-pre"),
                                    ),
                                    xs=12,
                                    md=6,
                                ),
                                dbc.Col(
                                    graph_block(
                                        ns("graph-post"),
                                        "Processed Signal",
                                        "OUT",
                                        ns("cursor-readout-post"),
                                    ),
                                    xs=12,
                                    md=6,
                                ),
                            ],
                            className="g-3",
                        ),
                    ],
                    className="cine-viewer-block",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        html.I(className="fas fa-play"),
                                        id=ns("play"),
                                        color="primary",
                                        outline=True,
                                        size="sm",
                                        title="Play",
                                    ),
                                    dbc.Button(
                                        html.I(className="fas fa-pause"),
                                        id=ns("pause"),
                                        color="primary",
                                        outline=True,
                                        size="sm",
                                        title="Pause",
                                    ),
                                    dbc.Button(
                                        html.I(className="fas fa-stop"),
                                        id=ns("stop"),
                                        color="primary",
                                        outline=True,
                                        size="sm",
                                        title="Stop & reset view",
                                    ),
                                    dbc.Button(
                                        html.I(className="fas fa-redo"),
                                        id=ns("loop"),
                                        color="secondary",
                                        outline=True,
                                        size="sm",
                                        title="Toggle loop / reset view",
                                    ),
                                ]
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(
                                        "Speed",
                                        className="speed-label mb-1",
                                    ),
                                    dcc.Slider(
                                        id=ns("speed"),
                                        min=0.25,
                                        max=2.0,
                                        step=0.25,
                                        value=1.0,
                                        marks={
                                            0.25: "0.25x",
                                            0.5: "0.5x",
                                            1.0: "1x",
                                            1.5: "1.5x",
                                            2.0: "2x",
                                        },
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": False,
                                        },
                                        className="speed-slider",
                                    ),
                                ],
                                className="w-100",
                            ),
                            xs=12,
                            sm=8,
                            md=6,
                            lg=4,
                            className="mt-3 mt-sm-0 flex-grow-1",
                        ),
                    ],
                    className="cine-controls align-items-center g-3 mt-3",
                ),
                dcc.Store(id=ns("window-state")),
                dcc.Store(id=ns("playback-state")),
                dcc.Store(id=ns("last-relayout")),
                dcc.Interval(id=ns("ticker"), interval=50, disabled=True),
            ],
            id=ns("root"),
        )

    # ------------------------------------------------------------------ #
    # Callback registration
    # ------------------------------------------------------------------ #
    def register_callbacks(self, app):
        ns = self._ns
        max_points = self.max_points

        # ---------- helper utilities ----------
        def _decimate(y):
            if y.size <= max_points:
                return y, 1
            stride = int(np.ceil(y.size / max_points))
            return y[::stride], stride

        def _make_time_axis(num_samples, sample_rate, offset_samples=0, stride=1):
            indices = offset_samples + np.arange(num_samples) * stride
            return indices / sample_rate

        def _compute_y_range(y):
            if y.size == 0:
                return [-1, 1]
            amplitude = max(abs(float(np.max(y))), abs(float(np.min(y))))
            padding = max(amplitude * 0.15, 0.25)
            limit = amplitude + padding
            return [-limit, limit]

        def _make_figure(time_axis, y_values, title):
            y_range = _compute_y_range(y_values)
            fig = go.Figure()
            fig.add_trace(
                go.Scattergl(
                    x=time_axis,
                    y=y_values,
                    mode="lines",
                    line=dict(width=1.2, color="#00d9ff"),
                    hoverinfo="x+y",
                    name=title,
                )
            )
            fig.update_layout(
                margin=dict(l=60, r=15, t=30, b=50),
                template="plotly_dark",
                xaxis=dict(
                    showgrid=False,
                    rangeslider=dict(visible=False),
                    title="Time (s)",
                ),
                yaxis=dict(
                    title="Amplitude",
                    range=y_range,
                    tickmode="auto",
                    nticks=9,
                    tickformat=".2f",
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.12)",
                    zeroline=True,
                    zerolinecolor="rgba(255,255,255,0.25)",
                ),
                hovermode="x unified",
                height=260,
            )
            return fig

        # ---------- initialisation ----------
        @app.callback(
            Output(ns("window-state"), "data"),
            Output(ns("playback-state"), "data"),
            Input("signal-data-store", "data"),
        )
        def _initialize_window(signal_store):
            if not signal_store:
                return no_update, no_update

            total_samples = len(signal_store["samples"])
            sample_rate = signal_store["sample_rate"]

            default_span_seconds = 2.0
            span_samples = max(1, int(default_span_seconds * sample_rate))
            window = {
                "start": 0,
                "end": min(span_samples, total_samples),
                "total": total_samples,
                "sample_rate": sample_rate,
            }
            playback = {
                "is_playing": False,
                "loop": False,
                "cursor": 0,
            }
            return window, playback

        # ---------- playback controls ----------
        @app.callback(
            Output(ns("playback-state"), "data", allow_duplicate=True),
            Input(ns("play"), "n_clicks"),
            Input(ns("pause"), "n_clicks"),
            Input(ns("stop"), "n_clicks"),
            Input(ns("loop"), "n_clicks"),
            State(ns("playback-state"), "data"),
            prevent_initial_call=True,
        )
        def _update_playback(play, pause, stop, loop_btn, playback):
            if playback is None:
                playback = {"is_playing": False, "loop": False, "cursor": 0}

            trigger = ctx.triggered_id
            if trigger == ns("play"):
                playback["is_playing"] = True
            elif trigger == ns("pause"):
                playback["is_playing"] = False
            elif trigger == ns("stop"):
                playback["is_playing"] = False
                playback["cursor"] = 0
            elif trigger == ns("loop"):
                playback["loop"] = not playback.get("loop", False)
            return playback

        @app.callback(
            Output(ns("window-state"), "data", allow_duplicate=True),
            Input(ns("stop"), "n_clicks"),
            Input(ns("loop"), "n_clicks"),
            State(ns("window-state"), "data"),
            State("signal-data-store", "data"),
            prevent_initial_call=True,
        )
        def _reset_view(stop, loop_btn, window, signal_store):
            if not ctx.triggered or not signal_store or window is None:
                return no_update

            total_samples = len(signal_store["samples"])
            sample_rate = signal_store["sample_rate"]
            default_span_seconds = 2.0
            span_samples = max(1, int(default_span_seconds * sample_rate))

            window["start"] = 0
            window["end"] = min(span_samples, total_samples)
            return window

        @app.callback(
            Output(ns("ticker"), "disabled"),
            Input(ns("playback-state"), "data"),
        )
        def _toggle_interval(playback):
            if not playback:
                return True
            return not playback.get("is_playing", False)

        # ---------- ticker advances window ----------
        @app.callback(
            Output(ns("window-state"), "data", allow_duplicate=True),
            Input(ns("ticker"), "n_intervals"),
            State(ns("window-state"), "data"),
            State(ns("playback-state"), "data"),
            State(ns("speed"), "value"),
            prevent_initial_call=True,
        )
        def _advance_window(_, window, playback, speed):
            if not window or not playback or not playback.get("is_playing"):
                return no_update

            sr = window["sample_rate"]
            span = window["end"] - window["start"]
            increment = max(1, int(sr * 0.05 * speed))

            new_start = window["start"] + increment
            new_end = window["end"] + increment

            if new_end >= window["total"]:
                if playback.get("loop"):
                    new_start = 0
                    new_end = min(span, window["total"])
                else:
                    new_start = max(0, window["total"] - span)
                    new_end = window["total"]

            window["start"] = new_start
            window["end"] = new_end
            return window

        # ---------- zoom/pan sync ----------
        @app.callback(
            Output(ns("window-state"), "data", allow_duplicate=True),
            Output(ns("last-relayout"), "data"),
            Input(ns("graph-pre"), "relayoutData"),
            Input(ns("graph-post"), "relayoutData"),
            State(ns("window-state"), "data"),
            State(ns("last-relayout"), "data"),
            prevent_initial_call=True,
        )
        def _sync_relayout(relayout_pre, relayout_post, window, last):
            trigger = ctx.triggered_id
            relayout = relayout_pre if trigger == ns("graph-pre") else relayout_post
            if relayout is None or window is None:
                return no_update, no_update

            window_changed = False
            last_changed = False
            new_last = last or {}

            if "xaxis.range[0]" in relayout and "xaxis.range[1]" in relayout:
                start_t = relayout["xaxis.range[0]"]
                end_t = relayout["xaxis.range[1]"]
                sr = window["sample_rate"]
                start_idx = max(0, int(start_t * sr))
                end_idx = min(window["total"], int(end_t * sr))
                if end_idx > start_idx and (
                        start_idx != window["start"] or end_idx != window["end"]
                ):
                    window["start"] = start_idx
                    window["end"] = end_idx
                    window_changed = True

            if relayout.get("yaxis.autorange"):
                if new_last.get("autorange") is not True or new_last.get("y_range") is not None:
                    new_last = {"y_range": None, "autorange": True}
                    last_changed = True
            elif "yaxis.range[0]" in relayout and "yaxis.range[1]" in relayout:
                y_range = [
                    float(relayout["yaxis.range[0]"]),
                    float(relayout["yaxis.range[1]"]),
                ]
                if new_last.get("y_range") != y_range or not new_last.get("autorange", False):
                    new_last = {"y_range": y_range, "autorange": False}
                    last_changed = True

            return (
                window if window_changed else no_update,
                new_last if last_changed else no_update,
            )

        # ---------- render figures ----------
        @app.callback(
            Output(ns("graph-pre"), "figure"),
            Output(ns("graph-post"), "figure"),
            Output(ns("cursor-readout-pre"), "children"),
            Output(ns("cursor-readout-post"), "children"),
            Input(ns("window-state"), "data"),
            Input(ns("last-relayout"), "data"),
            State("signal-data-store", "data"),
            State("processed-signal-store", "data"),
        )
        def _update_figures(window, last_state, original, processed):
            if not window or not original:
                empty = go.Figure().update_layout(template="plotly_dark")
                return empty, empty, "—", "—"

            start = window["start"]
            end = window["end"]
            sr = window["sample_rate"]

            if end <= start:
                empty = go.Figure().update_layout(template="plotly_dark")
                return empty, empty, "—", "—"

            y_pre_full = np.asarray(original["samples"], dtype=float)[start:end]
            y_pre, stride_pre = _decimate(y_pre_full)
            x_pre = _make_time_axis(
                y_pre.size, sr, offset_samples=start, stride=stride_pre
            )

            if processed and processed.get("samples"):
                y_post_full = np.asarray(processed["samples"], dtype=float)[start:end]
            else:
                y_post_full = y_pre_full

            y_post, stride_post = _decimate(y_post_full)
            x_post = _make_time_axis(
                y_post.size, sr, offset_samples=start, stride=stride_post
            )

            fig_pre = _make_figure(x_pre, y_pre, "Input signal")
            fig_post = _make_figure(x_post, y_post, "Output signal")

            synced_y = None
            force_autorange = False
            if isinstance(last_state, dict):
                synced_y = last_state.get("y_range")
                force_autorange = last_state.get("autorange", False)

            for fig in (fig_pre, fig_post):
                fig.update_layout(uirevision="cine-y-sync")

            if force_autorange:
                for fig in (fig_pre, fig_post):
                    fig.update_yaxes(range=None, autorange=True)
            elif synced_y is not None:
                for fig in (fig_pre, fig_post):
                    fig.update_yaxes(range=synced_y, autorange=False)

            readout = f"{start / sr:.3f}s → {end / sr:.3f}s"
            return fig_pre, fig_post, readout, readout
