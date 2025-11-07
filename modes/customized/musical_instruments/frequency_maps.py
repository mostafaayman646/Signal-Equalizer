"""
Musical Instruments Frequency Ranges
Based on fundamental frequencies and harmonics of common instruments.
"""

MUSICAL_INSTRUMENTS_MAP = {
    # Guitar: fundamental range + harmonics
    'slider-guitar': [
        (82, 1200),  # Fundamental range (E2 to D6)
        (2000, 4000)  # Important harmonics for brightness
    ],

    # Piano: very wide range
    'slider-piano': [
        (27, 4186)  # A0 to C8 - full piano range
    ],

    # Drums: low frequencies (kick) + attack frequencies (snare/hi-hat)
    'slider-drums': [
        (40, 150),  # Kick drum fundamentals
        (200, 500),  # Snare body
        (5000, 10000)  # Hi-hat and cymbals
    ],

    # Violin: mid-high range with strong harmonics
    'slider-violin': [
        (196, 3136),  # G3 to G7
        (4000, 8000)  # Upper harmonics
    ],

    # Flute: high range instrument
    'slider-flute': [
        (262, 2093),  # C4 to C7
        (3000, 6000)  # Harmonics
    ],

    # Bass: very low frequencies
    'slider-bass': [
        (41, 350),  # E1 to F4
        (500, 1000)  # Some harmonics
    ],

    # Trumpet: mid-high brass
    'slider-trumpet': [
        (165, 988),  # E3 to B5
        (1500, 3000)  # Bright harmonics
    ]
}