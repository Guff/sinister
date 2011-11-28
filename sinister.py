#!/usr/bin/env python

from sinister.viewport import Viewport
from sinister.ui.plot_area import PlotArea
from sinister.ui.plot_container import PlotContainer

from gi.repository import Gtk, Gdk
import cairo

from math import sin, gamma, lgamma

if __name__ == '__main__':
    viewport = Viewport(-10, 10, -10, 10, 1, 1)
    
    window = Gtk.Window()
    window.set_default_size(400, 300)
    
    plot = PlotArea(viewport)
    
    plot_container = PlotContainer(plot)
    
    window.add(plot_container)
    
    window.connect("delete-event", Gtk.main_quit)
    
    window.show_all()
    
    Gtk.main()
