import json
import os

def load_mode_config(mode):
    """Load slider configs for a mode from JSON"""
    # Define the modes that have dedicated files
    file_based_modes = ['Musical_Instruments', 'Animal_Sounds', 'Human_Voices','generic']

    if mode in file_based_modes:
        # Dynamically create filename based on mode
        json_filename = f"../Setting/{mode}_Frequency_Map.json"
        json_path = os.path.join(os.path.dirname(__file__), json_filename)
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Frequency map file not found at {json_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {json_path}")
            return {}
    else:
        # Handle other potential modes or error
        print(f"Warning: No frequency map defined for mode '{mode}'.")
        return {}
    
    # Data is now the root object for that mode, access 'sliders' directly
    return data.get('sliders', [])
