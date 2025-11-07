# ============================================================================
# modes/customized/animal_sounds/frequency_maps.py
# ============================================================================

"""
Animal Sounds Frequency Ranges
Based on typical frequency characteristics of animal vocalizations.
"""

ANIMAL_SOUNDS_MAP = {
    # Crow: mid-range harsh caws
    'slider-crow': [
        (500, 2000),  # Main vocalization range
        (3000, 5000)  # Harmonic content
    ],

    # Raccoon: chattering and growls
    'slider-raccoon': [
        (200, 800),  # Growls and low sounds
        (1500, 3000)  # Chatters and chirps
    ],

    # Peacock: loud high-pitched calls
    'slider-peacock': [
        (1000, 3000),  # Main call frequency
        (4000, 7000)  # Upper harmonics
    ],

    # Dog: barking range varies by size
    'slider-dog': [
        (400, 1500),  # Fundamental bark frequency
        (2000, 4000)  # Harmonics
    ],

    # Cat: meowing and purring
    'slider-cat': [
        (300, 900),  # Purring and low meows
        (1000, 2500),  # Main meow range
        (4000, 6000)  # High-pitched meows
    ],

    # Bird (generic): chirping
    'slider-bird': [
        (2000, 4000),  # Main chirping range
        (5000, 8000)  # Upper frequencies
    ],

    # Frog: croaking
    'slider-frog': [
        (100, 500),  # Low-frequency croaks
        (800, 1500)  # Some species have higher calls
    ],

    # Elephant: infrasound and rumbles
    'slider-elephant': [
        (14, 35),  # Infrasound (may not be audible)
        (100, 400),  # Audible rumbles
        (2000, 3000)  # Some vocalizations
    ]
}

