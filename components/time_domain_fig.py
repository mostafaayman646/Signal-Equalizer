import plotly.graph_objs as go


def create_time_figure(time, signal, title):#Main callbacks -----------------------------------------------------------------
    """Create time domain figure"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time, y=signal, mode='lines', line=dict(color='#00d9ff', width=1)))
    fig.update_layout(
        paper_bgcolor='#161821', plot_bgcolor='#161821',
        font=dict(color='#ffffff'),
        xaxis=dict(gridcolor='#2d3142', title='Time (s)'),
        yaxis=dict(gridcolor='#2d3142', title='Amplitude'),
        margin=dict(l=40, r=20, t=20, b=40),
        height=200, showlegend=False
    )
    return fig
