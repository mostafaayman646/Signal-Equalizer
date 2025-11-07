# ============================================================================
# modes/customized/human_voices/frequency_maps.py
# ============================================================================

"""
Human Voice Frequency Ranges
Based on gender, age, and fundamental frequency characteristics.
"""

HUMAN_VOICES_MAP = {
    # Adult Male: lower fundamental frequency
    'slider-male-1': [
        (85, 180),  # Fundamental frequency (F0)
        (300, 600),  # First formant
        (800, 2000),  # Second formant
        (2500, 3500)  # Third formant
    ],

    # Adult Female: higher fundamental
    'slider-female-1': [
        (165, 255),  # Fundamental frequency (F0)
        (400, 800),  # First formant
        (1000, 2500),  # Second formant
        (3000, 4500)  # Third formant
    ],

    # Child: highest fundamental
    'slider-child': [
        (250, 400),  # Fundamental frequency (F0)
        (500, 1000),  # First formant
        (1500, 3500),  # Second formant
        (4000, 6000)  # Third formant
    ],

    # Elderly Male: slightly lower than adult male
    'slider-elderly-male': [
        (80, 160),  # Fundamental frequency (F0)
        (280, 580),  # First formant
        (750, 1900),  # Second formant
        (2400, 3400)  # Third formant
    ],

    # Elderly Female: lower than adult female
    'slider-elderly-female': [
        (150, 240),  # Fundamental frequency (F0)
        (380, 780),  # First formant
        (950, 2400),  # Second formant
        (2900, 4400)  # Third formant
    ],

    # Bass Singer: very low male voice
    'slider-bass': [
        (80, 350),  # Extended lower range
        (250, 500),  # First formant
        (700, 1800),  # Second formant
        (2300, 3300)  # Third formant
    ],

    # Soprano Singer: very high female voice
    'slider-soprano': [
        (250, 1100),  # Extended upper range
        (500, 900),  # First formant
        (1200, 3000),  # Second formant
        (3500, 5000)  # Third formant
    ]
}
