import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

# Add this!
if current not in sys.path:
    sys.path.insert(0, current)

from modes.customized.customized_callbacks.process_sliders_callbacks import register_customized_callbacks
from modes.customized.customized_callbacks.Render_Ai_models_callbacks import register_ai_models
from modes.customized.customized_callbacks.Musical_Ai_model_callbacks import register_Musical_AiModel

__all__ = ['register_customized_callbacks','register_ai_models']