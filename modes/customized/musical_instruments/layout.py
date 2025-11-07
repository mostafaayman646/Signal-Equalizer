from components.base_template import create_base_layout

# Define slider configurations for musical instruments
slider_configs = [
    {
        'id': 'slider-guitar',
        'label': 'Guitar',
        'icon': 'fas fa-guitar',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-piano',
        'label': 'Piano',
        'icon': 'fas fa-piano',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-drums',
        'label': 'Drums',
        'icon': 'fas fa-drum',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-violin',
        'label': 'Violin',
        'icon': 'fas fa-music',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
    {
        'id': 'slider-flute',
        'label': 'Flute',
        'icon': 'fas fa-music',
        'min': 0,
        'max': 2,
        'value': 1,
        'step': 0.1
    },
]

# Create layout using base template
layout = create_base_layout(
    slider_configs=slider_configs,
    mode_name="Musical Instruments"
)
