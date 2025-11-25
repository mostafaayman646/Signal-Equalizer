import plotly.graph_objs as go
import numpy as np
from scipy.interpolate import interp1d

from Utils.Audiogram_scale import to_audiogram_axes


def safe_db(magnitude):
    """Convert magnitude to dB scale, handling zeros"""
    magnitude = np.array(magnitude)
    with np.errstate(divide='ignore', invalid='ignore'):
        db = 20 * np.log10(magnitude)
        db[~np.isfinite(db)] = -120  # Replace -inf and nan with -120 dB
    return db


def decimate_for_plotting(x, y, max_points=2000):
    """
    Decimate data for faster plotting while preserving shape.
    
    Args:
        x: X-axis data (frequencies)
        y: Y-axis data (magnitudes)
        max_points: Maximum number of points to plot
    
    Returns:
        decimated_x, decimated_y
    """
    if len(x) <= max_points:
        return x, y
    
    # Calculate decimation factor
    stride = int(np.ceil(len(x) / max_points))
    
    # Decimate
    x_decimated = x[::stride]
    y_decimated = y[::stride]
    
    return x_decimated, y_decimated

def create_freq_figure(freq, mag, use_db=True, max_points=2000, scale_mode="linear"):
    """
    Create frequency domain figure with optimizations.
    
    Args:
        freq: Frequency array
        mag: Magnitude array
        use_db: Convert to dB scale (default True)
        max_points: Maximum points to plot for performance
        scale_mode: 'linear' or 'audiogram'
    """
    # Convert to numpy arrays
    freq = np.array(freq)
    mag = np.array(mag)
    
    # Convert to dB scale if requested
    if use_db:
        mag_plot = safe_db(mag)
        y_label = 'Magnitude (dB)'
        y_range = [-120, np.max(mag_plot) + 10] if scale_mode != "audiogram" else None
    else:
        mag_plot = mag
        y_label = 'Magnitude'
        y_range = None
    
    # Decimate for faster plotting
    freq_decimated, mag_decimated = decimate_for_plotting(freq, mag_plot, max_points)
    
    axis_overrides = {}
    hover_text = None

    if scale_mode == "audiogram":
        (
            scaled_x,
            scaled_y,
            axis_overrides,
            hover_labels,
        ) = to_audiogram_axes(freq_decimated, mag_decimated)
        
        
        if len(scaled_x) and len(scaled_y):
            scaled_x_arr = np.array(scaled_x, dtype=float)
            scaled_y_arr = np.array(scaled_y, dtype=float)
            
            
            # Interpolate to create smooth curve between octave points
            try:
                f_interp = interp1d(scaled_x_arr, scaled_y_arr, kind='cubic', bounds_error=False, fill_value='extrapolate')
                
                # Generate interpolated points on log scale
                x_min, x_max = np.log10(scaled_x_arr.min()), np.log10(scaled_x_arr.max())
                x_log_interp = np.logspace(x_min, x_max, 200)
                y_interp = f_interp(x_log_interp)
                
                # Clamp y values to valid audiogram range [0, 120]
                y_interp = np.clip(y_interp, 0, 120)
                
                
                freq_decimated = x_log_interp
                mag_decimated = y_interp
            except Exception as e:
                print(f"[AUDIOGRAM DEBUG] Interpolation failed: {e}")
                import traceback
                traceback.print_exc()
                freq_decimated = scaled_x_arr
                mag_decimated = scaled_y_arr
            
            y_label = 'Audiogram dB HL'
        else:
            print(f"[AUDIOGRAM DEBUG] scaled_x or scaled_y is empty!")
            axis_overrides = {}
    
    # Create figure
    fig = go.Figure()
    
    
    trace_kwargs = dict(
        x=freq_decimated,
        y=mag_decimated,
        mode='lines',
        line=dict(color='#00d9ff', width=1.5),
        name='Magnitude'
    )

    scatter_class = go.Scattergl
    fig.add_trace(scatter_class(**trace_kwargs))
    
    xaxis_config = dict(
        gridcolor='#2d3142',
        title='Frequency (Hz)',
        showgrid=True
    )
    yaxis_config = dict(
        gridcolor='#2d3142',
        title=y_label,
        showgrid=True,
        range=y_range
    )

    if axis_overrides.get("xaxis"):
        xaxis_config.update(axis_overrides["xaxis"])
    if axis_overrides.get("yaxis"):
        yaxis_config.update(axis_overrides["yaxis"])

    fig.update_layout(
        paper_bgcolor='#161821',
        plot_bgcolor='#161821',
        font=dict(color='#ffffff'),
        xaxis=xaxis_config,
        yaxis=yaxis_config,
        margin=dict(l=40, r=20, t=20, b=40),
        height=300,
        showlegend=False,
        hovermode='x'
    )
    
    return fig