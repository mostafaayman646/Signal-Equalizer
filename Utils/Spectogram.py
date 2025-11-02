from scipy import signal

def make_spectogram(x,fs,one_sided = True):
    f, t, Sxx = signal.spectrogram(x, fs,return_onesided=one_sided)
    return f,t,Sxx

#For documentation page check: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html

#Example Usage in Dash
# import dash
# from dash import dcc, html, callback, Input, Output
# import plotly.graph_objects as go
# import numpy as np
# from scipy.fft import fftshift
# rng = np.random.default_rng()
# fs = 10e3
# N = 1e5
# amp = 2 * np.sqrt(2)
# noise_power = 0.01 * fs / 2
# time = np.arange(N) / float(fs)
# mod = 500*np.cos(2*np.pi*0.25*time)
# carrier = amp * np.sin(2*np.pi*3e3*time + mod)
# noise = rng.normal(scale=np.sqrt(noise_power), size=time.shape)
# noise *= np.exp(-time/5)
# x = carrier + noise
# f, t, Sxx = make_spectogram(x,fs)

# # Create Dash app
# app = dash.Dash(__name__)

# app.layout = html.Div([
#     html.H1('Spectrogram Visualization', style={'textAlign': 'center'}),
    
#     dcc.Graph(
#         id='spectrogram-plot',
#         figure=go.Figure(
#             data=go.Heatmap(
#                 x=t,
#                 y=f,
#                 z=Sxx,
#                 colorscale='Viridis'
#             ),
#             layout=go.Layout(
#                 title='Spectrogram',
#                 xaxis={'title': 'Time [sec]'},
#                 yaxis={'title': 'Frequency [Hz]'},
#                 height=600,
#                 width=650
#             )
#         )
#     )
# ])

# if __name__ == '__main__':
#     app.run(debug=True)