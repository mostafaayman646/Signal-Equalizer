import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

if current not in sys.path:
    sys.path.insert(0, current)

from dash import html
import dash_bootstrap_components as dbc


def create_ai_equalizer_button():
    """Creates a button to trigger the AI Equalizer feature"""
    
    return dbc.Button(
        [html.I(className="fas fa-robot me-2"), "Try AI Equalizer"],
        id='ai-equalizer-btn',
        color="info",
        size="lg",
        className="w-100"
    )