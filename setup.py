#!/usr/bin/env python3

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.sysconfig import PREFIX
from distutils.util import convert_path

schema_dir =  'share/glib-2.0/schemas'

data_files = [('share/sinister', ['data/sinister.ui']),
              (schema_dir, ['data/apps.sinister.gschema.xml'])]

class post_install(install_data):
    def run(self):
        super().run()
        
        self.spawn(['glib-compile-schemas', convert_path(PREFIX + '/' + schema_dir)])

setup(
    name        = 'sinister',
    cmdclass    = {'install_data': post_install},
    version     = '0.0.1',
    description = 'Simple plotting program',
    author      = 'Guff',
    scripts     = ['sinister_bin.py'],
    packages    = ['sinister', 'sinister.ui'],
    data_files  = data_files
)
