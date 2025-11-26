import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, ctx, no_update, Patch

# --- Performance Constants ---
MAX_POINTS_ON_SCREEN = 800  # Lower = Faster. 800 is usually plenty.
PLAYBACK_INTERVAL_MS = 80  # Higher = Less lag. 80ms is ~12fps (smooth for web).
DECIMALS = 2  # Rounding data reduces JSON size drastically.


def register_cine_viewer_callbacks(app):
    """
    Ultra-Light Cine Viewer Logic
    Optimized for smooth playback over HTTP.
    """

    # 1. Initialize Window & Set Optimal Ticker Speed
    @app.callback(
        Output('cine-window-state', 'data'),
        Output('cine-playback-state', 'data'),
        Output('cine-ticker', 'interval'),  # Optimize the interval dynamically
        Input('signal-data-store', 'data'),
    )
    def initialize_window(signal_store):
        if not signal_store:
            return no_update, no_update, no_update

        total = len(signal_store.get("samples", []))
        sr = signal_store.get("sample_rate", 44100)

        # Default view: 2 seconds
        span = max(1, int(2.0 * sr))

        window = {
            "start": 0,
            "end": min(span, total),
            "total": total,
            "sample_rate": sr,
        }
        playback = {"is_playing": False, "loop": False, "cursor": 0}

        # Return window, playback, and the optimized interval speed
        return window, playback, PLAYBACK_INTERVAL_MS

    # 2. Toggle Ticker
    @app.callback(
        Output('cine-ticker', 'disabled'),
        Input('cine-playback-state', 'data'),
    )
    def toggle_ticker(playback):
        if not playback: return True
        return not playback.get('is_playing', False)

    # 3. Playback Controls (Play/Pause/Stop/Loop)
    @app.callback(
        Output('cine-playback-state', 'data', allow_duplicate=True),
        Input('cine-play', 'n_clicks'),
        Input('cine-pause', 'n_clicks'),
        Input('cine-stop', 'n_clicks'),
        Input('cine-loop', 'n_clicks'),
        State('cine-playback-state', 'data'),
        State('cine-window-state', 'data'),
        prevent_initial_call=True
    )
    def update_playback(play, pause, stop, loop_btn, playback, window):
        trigger = ctx.triggered_id
        playback = playback.copy() if playback else {'is_playing': False, 'loop': False, 'cursor': 0}

        if trigger == 'cine-play':
            playback['is_playing'] = True
            # Restart if at end and not looping
            if window and window['end'] >= window['total'] and not playback.get('loop'):
                playback['cursor'] = 0
            # Sync cursor if fresh start
            elif window and not playback.get('is_playing'):
                playback['cursor'] = window['start']
        elif trigger == 'cine-pause':
            playback['is_playing'] = False
        elif trigger == 'cine-stop':
            playback['is_playing'] = False
            playback['cursor'] = 0
        elif trigger == 'cine-loop':
            playback['loop'] = not playback.get('loop', False)

        return playback

    # 4. Reset View Logic
    @app.callback(
        Output('cine-window-state', 'data', allow_duplicate=True),
        Input('cine-stop', 'n_clicks'),
        Input('cine-loop', 'n_clicks'),
        State('cine-window-state', 'data'),
        State('signal-data-store', 'data'),
        prevent_initial_call=True
    )
    def reset_view(stop, loop, window, signal_store):
        if not window or not signal_store: return no_update
        new_window = window.copy()
        span = new_window['end'] - new_window['start']
        new_window['start'] = 0
        new_window['end'] = min(span, new_window['total'])
        return new_window

    # 5. The Ticker Engine (Calculates new positions)
    @app.callback(
        Output('cine-window-state', 'data', allow_duplicate=True),
        Output('cine-playback-state', 'data', allow_duplicate=True),
        Input('cine-ticker', 'n_intervals'),
        State('cine-window-state', 'data'),
        State('cine-playback-state', 'data'),
        State('cine-speed', 'value'),
        prevent_initial_call=True
    )
    def advance_window(_, window, playback, speed):
        if not window or not playback or not playback.get('is_playing'):
            return no_update, no_update

        sr = window['sample_rate']
        # Calculate step size based on real-time Interval
        step_samples = int(sr * (PLAYBACK_INTERVAL_MS / 1000.0) * (speed or 1.0))

        current_start = window['start']
        span = window['end'] - window['start']
        total = window['total']

        new_start = current_start + step_samples
        new_end = new_start + span
        should_stop = False

        if new_end >= total:
            if playback.get('loop'):
                new_start = 0
                new_end = span
            else:
                new_start = total - span
                new_end = total
                should_stop = True

        window_out = window.copy()
        window_out['start'] = int(new_start)
        window_out['end'] = int(new_end)

        playback_out = playback.copy()
        playback_out['cursor'] = int(new_start)
        if should_stop:
            playback_out['is_playing'] = False

        return window_out, playback_out

    # 6. Optimized Renderer (Patch + Rounding + Decimation)
    @app.callback(
        Output('cine-graph-pre', 'figure'),
        Output('cine-graph-post', 'figure'),
        Input('cine-window-state', 'data'),
        Input('cine-last-relayout', 'data'),
        State('signal-data-store', 'data'),
        State('processed-signal-store', 'data'),
        State('cine-graph-pre', 'figure'),
        prevent_initial_call=True
    )
    def update_figures_optimized(window, last_state, original, processed, current_fig):
        trigger = ctx.triggered_id

        if not window or not original:
            return no_update, no_update

        # --- A. Smart Slicing & Decimation ---
        samples = np.asarray(original.get('samples', []), dtype=float)
        if len(samples) == 0: return no_update, no_update

        start = int(max(0, window['start']))
        end = int(min(len(samples), window['end']))

        # Calculate Step to strictly limit points on screen
        view_size = end - start
        step = max(1, view_size // MAX_POINTS_ON_SCREEN)

        # Slice and Round (Rounding significantly speeds up JSON transfer)
        y_pre = np.round(samples[start:end:step], DECIMALS)

        # Generate X Axis
        t_start = start / window['sample_rate']
        t_end = end / window['sample_rate']
        # Use linspace for fastest array generation
        x_axis = np.linspace(t_start, t_end, len(y_pre))
        x_axis = np.round(x_axis, 3)  # Round time axis too

        # Handle Output Signal
        y_post = None
        x_post = None
        if processed and 'samples' in processed:
            proc_s = np.asarray(processed['samples'], dtype=float)
            if len(proc_s) > 0:
                p_end = min(end, len(proc_s))
                y_post = np.round(proc_s[start:p_end:step], DECIMALS)
                x_post = np.linspace(t_start, p_end / window['sample_rate'], len(y_post))
                x_post = np.round(x_post, 3)

        # --- B. Update Check (Patch vs Full) ---
        graph_exists = current_fig and 'data' in current_fig and len(current_fig['data']) > 0
        is_playback = (trigger == 'cine-window-state')

        if is_playback and graph_exists:
            # === Fast Patch Update ===
            patch_pre = Patch()
            patch_post = Patch()

            # Update Lines
            patch_pre['data'][0]['x'] = x_axis
            patch_pre['data'][0]['y'] = y_pre
            patch_pre['layout']['xaxis']['range'] = [t_start, t_end]

            if y_post is not None:
                patch_post['data'][0]['x'] = x_post
                patch_post['data'][0]['y'] = y_post
            else:
                patch_post['data'][0]['x'] = x_axis
                patch_post['data'][0]['y'] = y_pre

            patch_post['layout']['xaxis']['range'] = [t_start, t_end]

            return patch_pre, patch_post

        # === Full Figure Initialization ===
        def get_yrange(y):
            if len(y) == 0: return [-1, 1]
            mx = np.max(np.abs(y))
            return [-mx * 1.1, mx * 1.1]

        y_range_pre = get_yrange(y_pre)
        y_range_post = get_yrange(y_post) if y_post is not None else y_range_pre

        # Layout Configuration with uirevision to reduce flicker
        layout_cfg = dict(
            template="plotly_dark",
            margin=dict(l=40, r=10, t=10, b=30),
            paper_bgcolor='#12172e',
            plot_bgcolor='#12172e',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', range=[t_start, t_end]),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', zeroline=True),
            height=260,
            uirevision='true'  # Keep camera/zoom state stable
        )

        fig_pre = go.Figure()
        fig_pre.add_trace(go.Scattergl(
            x=x_axis, y=y_pre, mode='lines',
            line=dict(color='#00d9ff', width=1.5), name='Input'
        ))
        fig_pre.update_layout(**layout_cfg)
        fig_pre.update_yaxes(range=y_range_pre)

        fig_post = go.Figure()
        data_post = y_post if y_post is not None else y_pre
        color_post = '#00ff88' if y_post is not None else '#00d9ff'
        x_post_final = x_post if y_post is not None else x_axis

        fig_post.add_trace(go.Scattergl(
            x=x_post_final, y=data_post, mode='lines',
            line=dict(color=color_post, width=1.5), name='Output'
        ))
        fig_post.update_layout(**layout_cfg)
        fig_post.update_yaxes(range=y_range_post)

        return fig_pre, fig_post

    # 7. Sync Zoom/Pan
    @app.callback(
        Output('cine-window-state', 'data', allow_duplicate=True),
        Output('cine-last-relayout', 'data'),
        Input('cine-graph-pre', 'relayoutData'),
        Input('cine-graph-post', 'relayoutData'),
        State('cine-window-state', 'data'),
        State('cine-last-relayout', 'data'),
        prevent_initial_call=True
    )
    def sync_relayout(rel_pre, rel_post, window, last):
        trig = ctx.triggered_id
        relayout = rel_pre if trig == 'cine-graph-pre' else rel_post
        if not relayout or not window: return no_update, no_update

        if 'xaxis.range[0]' in relayout:
            t0 = relayout['xaxis.range[0]']
            t1 = relayout['xaxis.range[1]']
            sr = window['sample_rate']
            new_window = window.copy()
            new_window['start'] = int(t0 * sr)
            new_window['end'] = int(t1 * sr)
            return new_window, no_update

        return no_update, no_update