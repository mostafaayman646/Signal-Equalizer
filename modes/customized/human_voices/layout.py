"""
Human Voices Mode Layout
Uses JSON configuration file for frequency mappings
"""

from components.base_template import create_base_layout
from modes.customized.frequency_map_loader import get_slider_configs

# Get slider configurations from JSON file
slider_configs = get_slider_configs('voices')

# Create layout using base template
layout = create_base_layout(
    slider_configs=slider_configs,
    mode_name="Human Voices"
)
