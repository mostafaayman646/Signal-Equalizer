import plotly.graph_objs as go
import numpy as np


def create_spec_figure(f, t, Sxx):
    """
    Creates a Plotly figure for the spectrogram with proper sizing
    """

    epsilon = 1e-10
    Sxx_db = 10 * np.log10(Sxx + epsilon)

    trace = go.Heatmap(
        x=t,
        y=f,
        z=Sxx_db,
        colorscale='Inferno',
        colorbar=dict(
            title=dict(
                text='Intensity [dB]',
                side='right'  # This is the correct way to position the title
            ),
            thickness=15,
            len=0.7,
            x=1.02,  # Position colorbar to the right
            xanchor='left'
        ),
        zsmooth='best'
    )

    layout = go.Layout(
        xaxis=dict(
            title='Time [sec]',
            gridcolor='rgba(255,255,255,0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title='Frequency [Hz]',
            range=[0, f.max()],
            gridcolor='rgba(255,255,255,0.1)',
            showgrid=True
        ),
        paper_bgcolor='#12172e',
        plot_bgcolor='#12172e',
        font=dict(color='#ffffff', size=10),
        margin=dict(l=50, r=50, t=10, b=40),
        autosize=True,
        hovermode='closest'
    )

    fig = go.Figure(data=[trace], layout=layout)

    return fig