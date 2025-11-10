import plotly.graph_objs as go

def create_spec_figure(f, t, Sxx):
    """Create spectrogram figure"""
    # Sxx_db = 10 * np.log10(Sxx + 1e-10)
    fig = go.Figure(data=go.Heatmap(z=Sxx, x=t, y=f, colorscale='Viridis'))
    fig.update_layout(
        paper_bgcolor='#161821', plot_bgcolor='#161821',
        font=dict(color='#ffffff', size=8),
        xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False),
        margin=dict(l=5, r=5, t=5, b=5), height = 300, width = 325
    )
    return fig