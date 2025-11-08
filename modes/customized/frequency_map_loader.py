import json
import os


def load_frequency_map(mode):
    """
    Loads frequency map from JSON file for the specified mode.

    Args:
        mode: String identifier ('instruments', 'animals', 'voices')

    Returns:
        dict: Frequency map with slider IDs as keys and frequency ranges as values

    Example return:
    {
        'slider-guitar': [[82, 1200], [2000, 4000]],
        'slider-piano': [[27, 4186]]
    }
    """
    # Map mode names to JSON filenames
    mode_files = {
        'instruments': 'musical_instruments.json',
        'animals': 'animal_sounds.json',
        'voices': 'human_voices.json'
    }

    if mode not in mode_files:
        raise ValueError(f"Unknown mode: {mode}. Must be one of {list(mode_files.keys())}")

    # Get path to JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'frequency_maps', mode_files[mode])

    # Load JSON file
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Frequency map file not found: {json_path}\n"
            f"Please ensure the file exists in modes/customized/frequency_maps/"
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {json_path}: {e}")

    # Convert JSON format to internal format
    frequency_map = {}

    for source in data['sources']:
        slider_id = source['id']
        frequency_ranges = source['frequency_ranges']

        # Validate frequency ranges
        for freq_range in frequency_ranges:
            if len(freq_range) != 2:
                raise ValueError(
                    f"Invalid frequency range for {slider_id}: {freq_range}. "
                    f"Must be [start, end]"
                )
            if freq_range[0] >= freq_range[1]:
                raise ValueError(
                    f"Invalid frequency range for {slider_id}: {freq_range}. "
                    f"Start frequency must be less than end frequency"
                )

        frequency_map[slider_id] = frequency_ranges

    return frequency_map


def get_slider_configs(mode):
    """
    Gets slider configurations from JSON file for layout creation.

    Args:
        mode: String identifier ('instruments', 'animals', 'voices')

    Returns:
        list: List of slider configuration dictionaries

    Example return:
    [
        {
            'id': 'slider-guitar',
            'label': 'Guitar',
            'icon': 'fas fa-guitar',
            'min': 0,
            'max': 2,
            'value': 1,
            'step': 0.1
        }
    ]
    """
    # Map mode names to JSON filenames
    mode_files = {
        'instruments': 'musical_instruments.json',
        'animals': 'animal_sounds.json',
        'voices': 'human_voices.json'
    }

    if mode not in mode_files:
        raise ValueError(f"Unknown mode: {mode}")

    # Get path to JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'frequency_maps', mode_files[mode])

    # Load JSON file
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Extract slider configurations
    slider_configs = []

    for source in data['sources']:
        config = {
            'id': source['id'],
            'label': source['label'],
            'icon': source.get('icon', 'fas fa-music'),
            'min': source.get('min', 0),
            'max': source.get('max', 2),
            'value': source.get('default_value', 1),
            'step': source.get('step', 0.1)
        }
        slider_configs.append(config)

    return slider_configs


def validate_frequency_map_file(json_path):
    """
    Validates a frequency map JSON file.

    Args:
        json_path: Path to JSON file

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Check required fields
        if 'mode' not in data:
            return False, "Missing 'mode' field"

        if 'sources' not in data:
            return False, "Missing 'sources' field"

        if not isinstance(data['sources'], list):
            return False, "'sources' must be a list"

        # Validate each source
        for idx, source in enumerate(data['sources']):
            required_fields = ['id', 'label', 'frequency_ranges']

            for field in required_fields:
                if field not in source:
                    return False, f"Source {idx}: Missing '{field}' field"

            # Validate frequency ranges
            if not isinstance(source['frequency_ranges'], list):
                return False, f"Source {idx}: 'frequency_ranges' must be a list"

            for range_idx, freq_range in enumerate(source['frequency_ranges']):
                if len(freq_range) != 2:
                    return False, f"Source {idx}, Range {range_idx}: Must have exactly 2 values [start, end]"

                if freq_range[0] >= freq_range[1]:
                    return False, f"Source {idx}, Range {range_idx}: Start must be < End"

        return True, "Valid"

    except Exception as e:
        return False, str(e)
