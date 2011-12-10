#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

from sinister.ui.windows import SinisterMainWindow

def main():
    window = SinisterMainWindow()    
    window.show_all()
    
    Gtk.main()

if __name__ == '__main__':
    main()
