from components.base_template import create_base_layout
from dash import html

# Define slider configurations for animal sounds
slider_configs = [
    {
        'id': 'slider-crow',
        'label': 'Crow',
        'icon': '/assets/icons/crow.png',  # Custom image
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-raccoon',
        'label': 'Raccoon',
        'icon': '/assets/icons/raccoon.png',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-peacock',
        'label': 'Peacock',
        'icon': '/assets/icons/peacock.png',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-dog',
        'label': 'Dog',
        'icon': 'fas fa-dog',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-cat',
        'label': 'Cat',
        'icon': 'fas fa-cat',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
]

# Create layout using base template
layout = create_base_layout(
    slider_configs=slider_configs,
    mode_name="Animal Sounds"
)