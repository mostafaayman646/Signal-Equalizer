import plotly.graph_objs as go
import numpy as np

def create_spec_figure(f, t, Sxx):
    """
    Creates a Plotly figure for the spectrogram, styled similarly
    to the user's matplotlib example.
    
    Args:
        f (np.array): Array of frequency bins (y-axis).
        t (np.array): Array of time bins (x-axis).
        Sxx (np.array): The 2D spectrogram matrix (power).
        
    Returns:
        go.Figure: A Plotly figure object.
    """
    
    # --- Start of Matplotlib-style changes ---
    
    # 1. Add a tiny "epsilon" to Sxx to avoid log(0) which is -infinity
    # This is a standard practice.
    epsilon = 1e-10 
    
    # 2. Convert power (Sxx) to decibels (dB)
    Sxx_db = 10 * np.log10(Sxx + epsilon)
    
    # 3. Create the Heatmap trace (the Plotly version of pcolormesh)
    trace = go.Heatmap(
        x=t,
        y=f,
        z=Sxx_db,
        colorscale='Inferno', # 'Viridis', 'Jet', 'Inferno' are good choices
        
        # 4. Set the colorbar title
        colorbar=dict(
            title='Intensity [dB]'
        ),
        
        # This makes the plot smoother, similar to 'gouraud' shading
        zsmooth='best' 
    )
    
    # 5. Create the layout and set labels (xlabel, ylabel, title)
    layout = go.Layout(
        title='Spectrogram',
        xaxis=dict(title='Time [sec]'),
        yaxis=dict(
            title='Frequency [Hz]',
            range=[0, f.max()]  # Similar to plt.ylim([0, samplerate / 2])
        ),
        plot_bgcolor='white',  # Set background to white
        paper_bgcolor='white',
    )
    
    # 6. Create the figure object
    fig = go.Figure(data=[trace], layout=layout)
    
    # 7. Add gridlines (similar to plt.grid(True))
    fig.update_layout(
        xaxis_showgrid=True, 
        yaxis_showgrid=True,
        xaxis_gridcolor='rgba(0, 0, 0, 0.1)', # Light grey grid
        yaxis_gridcolor='rgba(0, 0, 0, 0.1)',
        font_color='black' # Ensure text is readable on white bg
    )
    
    # --- End of Matplotlib-style changes ---
    
    return fig