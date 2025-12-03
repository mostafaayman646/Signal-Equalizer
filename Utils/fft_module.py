import importlib.util
import os
import sys

current = os.path.abspath(__file__)
while not os.path.exists(os.path.join(current, 'assets')):
    current = os.path.dirname(current)

# Add this!
if current not in sys.path:
    sys.path.insert(0, current)
def fft():

    pyd_file = os.path.join(current, 'assets', 'build', 'lib.win-amd64-cpython-313', 'fft_module.cp313-win_amd64.pyd')
    spec = importlib.util.spec_from_file_location("fft_module", pyd_file)
    fft_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fft_module)
    return fft_module