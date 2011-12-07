#!/usr/bin/env python

from sinister.config import conf
from sinister.viewport import Viewport
from sinister.plotters import PlotBg

from sinister.ui.plot_area import PlotArea
from sinister.ui.plot_container import PlotContainer

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk
import cairo

from math import sin, gamma, lgamma


def main():
    viewport = Viewport(conf.viewport.default_min_x,
                        conf.viewport.default_max_x,
                        conf.viewport.default_min_y,
                        conf.viewport.default_max_y)
    
    window = Gtk.Window()
    if conf.window.maximize_on_start:
        window.maximize()
    else:
        window.set_default_size(conf.window.default_width,
                                conf.window.default_height)
    
    plot_bg = PlotBg(viewport)
    plot = PlotArea(viewport, plot_bg)
    
    plot_container = PlotContainer(plot)
    
    window.add(plot_container)
    
    window.connect("delete-event", Gtk.main_quit)
    
    window.show_all()
    
    Gtk.main()

if __name__ == '__main__':
    main()
