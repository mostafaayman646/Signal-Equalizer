import plotly.graph_objs as go
import numpy as np


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

def create_freq_figure(freq, mag, use_db=True, max_points=2000):
    """
    Create frequency domain figure with optimizations.
    
    Args:
        freq: Frequency array
        mag: Magnitude array
        use_db: Convert to dB scale (default True)
        max_points: Maximum points to plot for performance
    """
    # Convert to numpy arrays
    freq = np.array(freq)
    mag = np.array(mag)
    
    # Convert to dB scale if requested
    if use_db:
        mag_plot = safe_db(mag)
        y_label = 'Magnitude (dB)'
        y_range = [-120, np.max(mag_plot) + 10]
    else:
        mag_plot = mag
        y_label = 'Magnitude'
        y_range = None
    
    # Decimate for faster plotting
    freq_decimated, mag_decimated = decimate_for_plotting(freq, mag_plot, max_points)
    
    # Create figure
    fig = go.Figure()
    
    # Use Scattergl for better performance with large datasets
    fig.add_trace(go.Scattergl(
        x=freq_decimated,
        y=mag_decimated,
        mode='lines',
        line=dict(color='#00d9ff', width=1.5),
        name='Magnitude'
    ))
    
    fig.update_layout(
        paper_bgcolor='#161821',
        plot_bgcolor='#161821',
        font=dict(color='#ffffff'),
        xaxis=dict(
            gridcolor='#2d3142',
            title='Frequency (Hz)',
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='#2d3142',
            title=y_label,
            showgrid=True,
            range=y_range
        ),
        margin=dict(l=40, r=20, t=20, b=40),
        height=300,
        showlegend=False,
        hovermode='x'
    )
    
    return fig