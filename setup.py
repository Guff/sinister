#!/usr/bin/env python3

from distutils.core import setup

data_files = [('share/sinister', ['data/sinister.ui'])]

setup(
    name        = 'sinister',
    version     = '0.0.1',
    description = 'Simple plotting program',
    author      = 'Guff',
    scripts     = ['sinister.py'],
    packages    = ['sinister', 'sinister.ui'],
    data_files  = data_files
)
