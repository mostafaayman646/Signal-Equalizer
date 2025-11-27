import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, ctx, no_update, html
from dash.exceptions import PreventUpdate

MAX_DISPLAY_POINTS = 3000  # Reduced for better performance
CURSOR_UPDATE_INTERVAL = 100  # Update every 100ms instead of 50ms for smoother performance


def register_cine_viewer_callbacks(app):
    """Register callbacks for synchronized cine viewer with audio playback"""

    # ============================================================================
    # 1. Initialize Full Signal Display
    # ============================================================================
    @app.callback(
        Output('cine-graph-pre', 'figure'),
        Output('cine-graph-post', 'figure'),
        Output('cine-playback-state', 'data'),
        Output('cine-window-state', 'data'),
        Input('signal-data-store', 'data'),
        Input('processed-signal-store', 'data'),
        prevent_initial_call=False
    )
    def initialize_full_signal(original_data, processed_data):
        """Display full signal on both graphs"""

        if not original_data:
            empty_fig = create_empty_figure()
            return empty_fig, empty_fig, None, None

        # Get original signal
        original_signal = np.array(original_data.get('samples', []), dtype=float)
        sample_rate = original_data.get('sample_rate', 44100)

        if len(original_signal) == 0:
            empty_fig = create_empty_figure()
            return empty_fig, empty_fig, None, None

        # Get processed signal (or use original if not available)
        if processed_data and processed_data.get('samples'):
            processed_signal = np.array(processed_data.get('samples', []), dtype=float)
        else:
            processed_signal = original_signal.copy()

        # Create time axis
        duration = len(original_signal) / sample_rate

        # Decimate for display
        original_decimated, time_decimated = decimate_signal(original_signal, sample_rate)
        processed_decimated, _ = decimate_signal(processed_signal, sample_rate)

        # Create figures
        fig_pre = create_signal_figure(
            time_decimated,
            original_decimated,
            "Original Signal",
            duration
        )

        fig_post = create_signal_figure(
            time_decimated,
            processed_decimated,
            "Processed Signal",
            duration
        )
        fig_pre.update_traces(line_color='#ffb800')
        fig_post.update_traces(line_color='#00ff88')
        # Initialize playback state
        playback_state = {
            'is_playing': False,
            'cursor_position': 0.0,  # in seconds
            'duration': duration,
            'audio_source': 'before'  # 'before' or 'after'
        }

        # Initialize window state for zoom sync
        window_state = {
            'x_range': [0, duration],
            'sample_rate': sample_rate,
            'total_samples': len(original_signal)
        }

        return fig_pre, fig_post, playback_state, window_state

    # ============================================================================
    # 2. Synchronized Zoom/Pan
    # ============================================================================
    @app.callback(
        Output('cine-graph-pre', 'figure', allow_duplicate=True),
        Output('cine-graph-post', 'figure', allow_duplicate=True),
        Output('cine-window-state', 'data', allow_duplicate=True),
        Input('cine-graph-pre', 'relayoutData'),
        Input('cine-graph-post', 'relayoutData'),
        Input('cine-zoom-in', 'n_clicks'),
        Input('cine-zoom-out', 'n_clicks'),
        Input('cine-zoom-reset', 'n_clicks'),
        State('cine-window-state', 'data'),
        State('cine-graph-pre', 'figure'),
        State('cine-graph-post', 'figure'),
        prevent_initial_call=True
    )
    def sync_zoom_pan(relayout_pre, relayout_post, btn_in, btn_out, btn_reset,
                      window_state, fig_pre, fig_post):
        """Synchronize zoom/pan between graphs AND handle zoom buttons"""

        if not window_state:
            raise PreventUpdate

        triggered = ctx.triggered_id

        # Current Signal Duration info
        total_duration = window_state.get('total_samples', 0) / window_state.get('sample_rate', 44100)
        current_range = window_state.get('x_range', [0, total_duration])

        new_min, new_max = current_range[0], current_range[1]
        range_changed = False

        # --- CASE 1: Zoom Buttons ---
        if triggered in ['cine-zoom-in', 'cine-zoom-out', 'cine-zoom-reset']:
            current_span = current_range[1] - current_range[0]
            center = (current_range[1] + current_range[0]) / 2

            if triggered == 'cine-zoom-in':
                # Zoom in by 20% (reduce span to 80%)
                new_span = current_span * 0.8
                new_min = center - (new_span / 2)
                new_max = center + (new_span / 2)

            elif triggered == 'cine-zoom-out':
                # Zoom out by 25% (increase span by 1.25)
                new_span = current_span * 1.25
                new_min = center - (new_span / 2)
                new_max = center + (new_span / 2)

                # Clamp to boundaries if zooming out too far
                if new_min < 0: new_min = 0
                if new_max > total_duration: new_max = total_duration

            elif triggered == 'cine-zoom-reset':
                new_min = 0
                new_max = total_duration

            range_changed = True

        # --- CASE 2: Mouse Interaction (Relayout) ---
        else:
            relayout_data = relayout_pre if triggered == 'cine-graph-pre' else relayout_post

            if relayout_data:
                # Handle Standard Zoom/Pan
                if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
                    new_min = relayout_data['xaxis.range[0]']
                    new_max = relayout_data['xaxis.range[1]']
                    range_changed = True

                # Handle Double-Click Autoscale
                elif 'xaxis.autorange' in relayout_data:
                    new_min = 0
                    new_max = total_duration
                    range_changed = True

        # --- Apply Changes ---
        if range_changed:
            # Update Window State
            window_state['x_range'] = [new_min, new_max]

            # Use Patch to update layouts efficiently (Optional but recommended)
            # Or manually update the dictionary as you were doing:
            fig_pre['layout']['xaxis']['range'] = [new_min, new_max]
            fig_post['layout']['xaxis']['range'] = [new_min, new_max]

            # Ensure Y-axis isn't messed up by autoscale
            if 'autorange' in fig_pre['layout']['xaxis']: del fig_pre['layout']['xaxis']['autorange']
            if 'autorange' in fig_post['layout']['xaxis']: del fig_post['layout']['xaxis']['autorange']

            return fig_pre, fig_post, window_state

        raise PreventUpdate

    # ============================================================================
    # 3. Playback Controls
    # ============================================================================
    @app.callback(
        Output('cine-playback-state', 'data', allow_duplicate=True),
        Output('cine-ticker', 'disabled'),
        Output('cine-loop', 'color'),
        Input('cine-play', 'n_clicks'),
        Input('cine-pause', 'n_clicks'),
        Input('cine-stop', 'n_clicks'),
        Input('cine-loop', 'n_clicks'),
        Input('cine-audio-source-toggle', 'value'),
        State('cine-playback-state', 'data'),
        prevent_initial_call=True
    )
    def control_playback(play_clicks, pause_clicks, stop_clicks, loop_clicks, audio_source, playback_state):
        """Handle playback controls"""

        if not playback_state:
            raise PreventUpdate

        triggered = ctx.triggered_id
        loop_color = 'success' if playback_state.get('loop', False) else 'secondary'

        if triggered == 'cine-play':
            playback_state['is_playing'] = True
            return playback_state, False, loop_color  # Enable ticker

        elif triggered == 'cine-pause':
            playback_state['is_playing'] = False
            return playback_state, True, loop_color  # Disable ticker

        elif triggered == 'cine-stop':
            playback_state['is_playing'] = False
            playback_state['cursor_position'] = 0.0
            return playback_state, True, loop_color  # Disable ticker

        elif triggered == 'cine-loop':
            playback_state['loop'] = not playback_state.get('loop', False)
            loop_color = 'success' if playback_state['loop'] else 'secondary'
            return playback_state, not playback_state['is_playing'], loop_color

        elif triggered == 'cine-audio-source-toggle':
            playback_state['audio_source'] = audio_source[0] if audio_source else 'before'
            return playback_state, not playback_state['is_playing'], loop_color

        raise PreventUpdate

    # ============================================================================
    # 4. Update Playback Cursor Position
    # ============================================================================
    @app.callback(
        Output('cine-playback-state', 'data', allow_duplicate=True),
        Input('cine-ticker', 'n_intervals'),
        State('cine-playback-state', 'data'),
        State('cine-speed', 'value'),
        prevent_initial_call=True
    )
    def advance_cursor(n_intervals, playback_state, speed):
        """Advance cursor position during playback - OPTIMIZED"""

        if not playback_state or not playback_state.get('is_playing'):
            raise PreventUpdate

        # Use larger time increment for smoother updates
        time_increment = CURSOR_UPDATE_INTERVAL / 1000.0 * (speed or 1.0)

        current_position = playback_state['cursor_position']
        duration = playback_state['duration']

        new_position = current_position + time_increment

        # Loop or stop at end
        if new_position >= duration:
            if playback_state.get('loop', False):
                new_position = 0.0
            else:
                new_position = duration
                playback_state['is_playing'] = False

        playback_state['cursor_position'] = new_position

        return playback_state

    # ============================================================================
    # 5. Draw Playback Cursor & Auto-Scroll (OPTIMIZED)
    # ============================================================================
    @app.callback(
        Output('cine-graph-pre', 'figure', allow_duplicate=True),
        Output('cine-graph-post', 'figure', allow_duplicate=True),
        Output('cine-current-time', 'children'),
        Output('cine-window-state', 'data', allow_duplicate=True),  # Added output to update zoom state
        Input('cine-playback-state', 'data'),
        State('cine-window-state', 'data'),  # Added state to know current zoom level
        State('cine-graph-pre', 'figure'),
        State('cine-graph-post', 'figure'),
        prevent_initial_call=True
    )
    def update_cursor_and_scroll(playback_state, window_state, fig_pre, fig_post):
        """Update cursor line AND auto-scroll graph if cursor moves out of view"""

        if not playback_state or not fig_pre or not fig_post:
            raise PreventUpdate

        cursor_position = playback_state.get('cursor_position', 0.0)
        duration = playback_state.get('duration', 1.0)

        # 1. Setup Patch for optimized updates
        from dash import Patch
        patch_pre = Patch()
        patch_post = Patch()

        # 2. AUTO-SCROLL LOGIC
        # ---------------------------------------------------------
        updated_window_state = no_update

        if window_state and 'x_range' in window_state:
            x_min, x_max = window_state['x_range']
            current_span = x_max - x_min

            # Only auto-scroll if we are actually zoomed in (span is less than full duration)
            # using a small tolerance (0.1s) for float comparison
            is_zoomed = current_span < (duration - 0.1)

            if is_zoomed:
                new_min, new_max = None, None

                # Case A: Cursor moved past the right edge (Progressing)
                # We trigger when cursor passes 95% of the view
                if cursor_position > (x_max - (current_span * 0.05)):
                    # Shift view so cursor is at 10% of the new screen (keep context)
                    new_min = cursor_position - (current_span * 0.1)
                    new_max = new_min + current_span

                # Case B: Cursor moved behind the left edge (Looping or Clicking back)
                elif cursor_position < x_min:
                    # Shift view so cursor is at the start
                    new_min = cursor_position
                    new_max = new_min + current_span

                # Apply the shift if needed
                if new_min is not None:
                    # Clamp to max duration
                    if new_max > duration:
                        new_max = duration
                        new_min = duration - current_span

                    # Clamp to 0
                    if new_min < 0:
                        new_min = 0
                        new_max = current_span

                    # Update the graphs
                    patch_pre['layout']['xaxis']['range'] = [new_min, new_max]
                    patch_post['layout']['xaxis']['range'] = [new_min, new_max]

                    # Update the state so the next callback knows where we are
                    window_state['x_range'] = [new_min, new_max]
                    updated_window_state = window_state
        # ---------------------------------------------------------

        # 3. Draw Cursor Line
        cursor_shape = {
            'type': 'line',
            'x0': cursor_position, 'x1': cursor_position,
            'y0': 0, 'y1': 1, 'yref': 'paper',
            'line': {'color': '#ff4757', 'width': 2},
            'layer': 'above'
        }

        # Initialize shapes list if it doesn't exist
        if 'shapes' not in fig_pre.get('layout', {}):
            patch_pre['layout']['shapes'] = []
        if 'shapes' not in fig_post.get('layout', {}):
            patch_post['layout']['shapes'] = []

        # Filter out old cursors
        shapes_pre = [s for s in fig_pre.get('layout', {}).get('shapes', [])
                      if s.get('line', {}).get('color') != '#ff4757']
        shapes_post = [s for s in fig_post.get('layout', {}).get('shapes', [])
                       if s.get('line', {}).get('color') != '#ff4757']

        # Add new cursor
        shapes_pre.append(cursor_shape)
        shapes_post.append(cursor_shape)

        patch_pre['layout']['shapes'] = shapes_pre
        patch_post['layout']['shapes'] = shapes_post

        # 4. Format time display
        time_display = format_time(cursor_position, duration)

        return patch_pre, patch_post, time_display, updated_window_state

    # ============================================================================
    # 6. Click to Seek Position
    # ============================================================================
    @app.callback(
        Output('cine-playback-state', 'data', allow_duplicate=True),
        Input('cine-graph-pre', 'clickData'),
        Input('cine-graph-post', 'clickData'),
        State('cine-playback-state', 'data'),
        prevent_initial_call=True
    )
    def seek_position(click_pre, click_post, playback_state):
        """Allow clicking on graph to seek to position"""

        if not playback_state:
            raise PreventUpdate

        triggered = ctx.triggered_id
        click_data = click_pre if triggered == 'cine-graph-pre' else click_post

        if not click_data or 'points' not in click_data:
            raise PreventUpdate

        # Get clicked x position (time)
        clicked_time = click_data['points'][0]['x']

        # Update cursor position
        playback_state['cursor_position'] = max(0, min(clicked_time, playback_state['duration']))

        return playback_state

    # ============================================================================
    # 7. Update Audio Player Source and Control Playback
    # ============================================================================
    @app.callback(
        Output('cine-audio-player', 'src'),
        Output('cine-audio-player', 'autoPlay'),
        Input('cine-audio-source-toggle', 'value'),
        Input('signal-data-store', 'data'),
        Input('processed-signal-store', 'data'),
        State('cine-playback-state', 'data'),
        prevent_initial_call=False
    )
    def update_audio_source(audio_source_toggle, original_data, processed_data, playback_state):
        """Update audio player source based on selected audio"""

        if not original_data:
            raise PreventUpdate

        # Determine which audio source to use
        audio_source = audio_source_toggle[0] if audio_source_toggle else 'before'

        triggered = ctx.triggered_id

        # Debug print to see what's happening
        print(f"[AUDIO SOURCE] Triggered by: {triggered}")
        print(f"[AUDIO SOURCE] Selected: {audio_source}")
        print(f"[AUDIO SOURCE] Has processed data: {bool(processed_data and processed_data.get('samples'))}")

        # Get appropriate signal
        if audio_source == 'a' and processed_data and processed_data.get('samples'):
            signal = np.array(processed_data.get('samples', []))
            sample_rate = processed_data.get('sample_rate', 44100)
            print(f"[AUDIO SOURCE] Using PROCESSED signal ({len(signal)} samples)")
        else:
            signal = np.array(original_data.get('samples', []))
            sample_rate = original_data.get('sample_rate', 44100)
            print(f"[AUDIO SOURCE] Using ORIGINAL signal ({len(signal)} samples)")

        if len(signal) == 0:
            raise PreventUpdate

        # Convert to base64 audio
        from Utils import audio_to_base64_uri
        audio_uri = audio_to_base64_uri(signal, sample_rate, normalize=True)

        # Autoplay if currently playing
        auto_play = playback_state and playback_state.get('is_playing', False) if playback_state else False

        print(f"[AUDIO SOURCE] Generated audio URI (length: {len(audio_uri)}), autoPlay: {auto_play}")

        return audio_uri, auto_play

    # ============================================================================
    # 9. Force Audio Reload When Processed Signal Updates
    # ============================================================================
    @app.callback(
        Output('cine-audio-player', 'src', allow_duplicate=True),
        Input('processed-signal-store', 'data'),
        State('cine-audio-source-toggle', 'value'),
        State('signal-data-store', 'data'),
        prevent_initial_call=True
    )
    def reload_audio_on_process(processed_data, audio_source_toggle, original_data):
        """Reload audio when processed signal updates and 'After' is selected"""

        if not processed_data or not original_data:
            raise PreventUpdate

        # Only update if "After" is currently selected
        audio_source = audio_source_toggle[0] if audio_source_toggle else 'before'

        if audio_source != 'a':
            print("[AUDIO RELOAD] Processed signal updated but 'Before' is selected - skipping")
            raise PreventUpdate

        print("[AUDIO RELOAD] Processed signal updated - reloading 'After' audio")

        # Get processed signal
        signal = np.array(processed_data.get('samples', []))
        sample_rate = processed_data.get('sample_rate', 44100)

        if len(signal) == 0:
            raise PreventUpdate

        # Convert to base64 audio
        from Utils import audio_to_base64_uri
        audio_uri = audio_to_base64_uri(signal, sample_rate, normalize=True)

        print(f"[AUDIO RELOAD] Reloaded processed audio ({len(signal)} samples)")

        return audio_uri
    # ============================================================================
    app.clientside_callback(
        """
        function(playback_state, speed) {
            if (!playback_state) return window.dash_clientside.no_update;
            
            const audio = document.getElementById('cine-audio-player');
            if (!audio) return window.dash_clientside.no_update;
            
            const isPlaying = playback_state.is_playing;
            const cursorPosition = playback_state.cursor_position || 0;
            
            // Set playback rate
            if (speed) {
                audio.playbackRate = speed;
            }
            
            // Control playback
            if (isPlaying) {
                // Sync time if significantly different
                if (Math.abs(audio.currentTime - cursorPosition) > 0.5) {
                    audio.currentTime = cursorPosition;
                }
                
                // Play if paused
                if (audio.paused) {
                    audio.play().catch(err => console.log('Play failed:', err));
                }
            } else {
                // Pause if playing
                if (!audio.paused) {
                    audio.pause();
                }
                // Sync time when paused
                audio.currentTime = cursorPosition;
            }
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('cine-audio-player', 'title'),
        Input('cine-playback-state', 'data'),
        Input('cine-speed', 'value'),
        prevent_initial_call=True
    )

    # ============================================================================
    # 10. Update Audio Track Label
    # ============================================================================
    @app.callback(
        Output('cine-audio-track-label', 'children'),
        Input('cine-audio-source-toggle', 'value'),
        prevent_initial_call=False
    )
    def update_track_label(audio_source_toggle):
        """Update label showing which track is playing"""
        audio_source = audio_source_toggle[0] if audio_source_toggle else 'before'

        if audio_source == 'a':
            return "Processed (After Equalization)"
        else:
            return "Original (Before Equalization)"

def decimate_signal(signal, sample_rate, max_points=MAX_DISPLAY_POINTS):
    """Decimate signal for efficient display - OPTIMIZED"""
    if len(signal) <= max_points:
        time = np.arange(len(signal)) / sample_rate
        return signal, time

    # Use downsampling with local averaging for smoother appearance
    stride = int(np.ceil(len(signal) / max_points))

    # Reshape and average for anti-aliasing effect
    trimmed_length = (len(signal) // stride) * stride
    signal_trimmed = signal[:trimmed_length]

    # Reshape and take mean
    signal_reshaped = signal_trimmed.reshape(-1, stride)
    decimated_signal = signal_reshaped.mean(axis=1)

    # Create time axis
    time = np.arange(len(decimated_signal)) * stride / sample_rate

    return decimated_signal, time


def create_signal_figure(time, signal, title, duration):
    """Create a plotly figure for signal display - OPTIMIZED"""

    # Calculate y-range
    if len(signal) > 0:
        y_max = max(abs(np.max(signal)), abs(np.min(signal)))
        y_range = [-y_max * 1.1, y_max * 1.1]
    else:
        y_range = [-1, 1]

    fig = go.Figure()

    # Use Scattergl for better performance
    fig.add_trace(go.Scattergl(
        x=time,
        y=signal,
        mode='lines',
        line=dict(color='#00d9ff', width=1),
        name=title,
        hovertemplate='Time: %{x:.3f}s<br>Amplitude: %{y:.3f}<extra></extra>'
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#12172e',
        plot_bgcolor='#12172e',
        font=dict(color='#ffffff', size=10),
        xaxis=dict(
            title='Time (s)',
            range=[0, duration],
            showgrid=True,
            gridcolor='rgba(255,255,255,0.08)',
            zeroline=False,
            fixedrange=False  # Allow zooming
        ),
        yaxis=dict(
            title='Amplitude',
            range=y_range,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.08)',
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.2)',
            fixedrange=False  # Allow zooming
        ),
        margin=dict(l=45, r=15, t=25, b=35),
        height=260,
        hovermode='x unified',
        uirevision='constant',  # Preserve UI state
        # Performance optimizations
        dragmode='pan',
        modebar=dict(
            remove=['lasso2d', 'select2d']
        )
    )

    return fig


def create_empty_figure():
    """Create empty placeholder figure"""
    fig = go.Figure()

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#12172e',
        plot_bgcolor='#12172e',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[{
            'text': 'Upload audio to begin',
            'xref': 'paper',
            'yref': 'paper',
            'x': 0.5,
            'y': 0.5,
            'showarrow': False,
            'font': {'size': 16, 'color': '#666'}
        }]
    )

    return fig


def format_time(current, total):
    """Format time display as MM:SS / MM:SS"""
    def to_mmss(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    return f"{to_mmss(current)} / {to_mmss(total)}"
