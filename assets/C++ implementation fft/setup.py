from setuptools import setup, Extension
import pybind11
import numpy

ext_modules = [
    Extension(
        'fft_module',
        ['fft_module.cpp'],
        include_dirs=[
            pybind11.get_include(),
            numpy.get_include()
        ],
        language='c++',
        extra_compile_args=['/std:c++14'] if __import__('platform').system() == 'Windows' else ['-std=c++14'],
    ),
]

setup(
    name='fft_module',
    version='1.0',
    ext_modules=ext_modules,
    zip_safe=False,
)