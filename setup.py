#!/usr/bin/env python3

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension('sinister.cplottable', ['sinister/cplottable.pyx']),
               Extension('sinister.cplotters', ['sinister/cplotters.pyx'])]

setup(
    name        = 'sinister',
    version     = '0.0.1',
    description = 'Simple plotting program',
    author      = 'Guff',
    scripts     = ['sinister.py'],
    packages    = ['sinister'],
    cmdclass    = {'build_ext': build_ext},
    ext_modules = ext_modules
)
