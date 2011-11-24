#! /usr/bin/env python

from gi.repository import Gtk as gtk, Gdk as gdk
import cairo

from math import sin, gamma, lgamma

def frange(start, stop=None, step=1):
    if stop is None:
        start, stop = 0, start
    
    r = start
    while r <= stop - step / 2:
        yield r
        r += step

class Viewport(object):
    def __init__(self, min_x, max_x, min_y, max_y):
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y

class PlotConf(object):
    def __init__(self, width, height, min_step=0.5, max_step=3):
        self.width, self.height = width, height
        self.min_step, self.max_step = min_step, max_step

class Plottable(object):
    def __init__(self):
        self.viewport = None
        self.width, self.height = None, None        
        
        self.surface = None
    
    def draw(self):
        pass
    
    def set_viewport(self, viewport):
        self.viewport = viewport
    
    def resize(self, width, height):
        if self.width == width and self.height == height:
            return
        
        self.width, self.height = width, height
        
        if self.surface is not None:
            self.surface.finish()
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
    
    def plot(self, cr):
        cr.set_source_surface(self.surface)
        cr.paint()
    
    def coords_to_window(self, px, py):
        min_x, max_x = self.viewport.min_x, self.viewport.max_x
        min_y, max_y = self.viewport.min_y, self.viewport.max_y
        width, height = self.width, self.height
        wx = (px - min_x) * width / (max_x - min_x)
        wy = (py - max_y) * height / (min_y - max_y)
        
        return (wx, wy)
    
    def window_to_coords(self, wx):
        min_x, max_x = self.viewport.min_x, self.viewport.max_x
        width = self.width
        
        return (max_x - min_x) * wx / width + min_x

class FunctionPlot(Plottable):
    def __init__(self, func):
        super().__init__()
        
        self.func = func
    
    def draw(self):
        cr = cairo.Context(self.surface)
        cr.set_line_width(1.0)
        
        for window_x in range(self.width + 1):
            window_y = self(window_x)
            if window_y is None:
                continue
            
            cr.line_to(window_x, window_y)
        
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()
    
    def derivative(self, x):
        x_scale = self.width / (self.max_x - self.min_x)
        delta = x_scale * self.min_step / 2
        
        try:
            return (self.func(x + delta) - self.func(x - delta)) / (2 * delta)
        except:
            return None
    
    def get_value_and_step(self, x):
        y = None
        try:
            y = self.func(x)
        except:
            return (None, self.min_step)
        
        y_scale = self.height / (self.max_y - self.min_y)
        aspect = self.width / self.height
        dy = abs(self.derivative(self, x))
        
        if dy > y_scale * self.max_step:
            return (y, self.min_step)
        else:
            return (y, self.max_step)
    
    def __call__(self, window_x):
        plot_x = self.window_to_coords(window_x)
        try:
            plot_y = self.func(plot_x)
            x, y = self.coords_to_window(0, plot_y)
            return y
        except:
            return None

class PlotBg(Plottable):
    def draw(self):
        origin_x, origin_y = self.coords_to_window(0, 0)
        
        cr = cairo.Context(self.surface)
        
        cr.set_source_rgb(1, 1, 1)
        cr.paint()
        
        cr.move_to(0, origin_y)
        cr.line_to(self.width, origin_y)
        
        cr.move_to(origin_x, 0)
        cr.line_to(origin_x, self.height)
        
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

class PlotArea(gtk.DrawingArea):
    def __init__(self, viewport):
        super().__init__()
        
        self.viewport = viewport
        
        self.width, self.height = None, None
        
        self.plot_bg = PlotBg()
        self.plot_bg.set_viewport(self.viewport)
        
        self.plots = []
        
        def delete_event(widget, event):
            gtk.main_quit()
            return False
        
        def draw_event(widget, cr):
            widget.plot(cr)
            
            return False
        
        def configure_event(widget, event):
            if event.width == widget.width or event.height == widget.height:
                return True
            
            widget.width = event.width
            widget.height = event.height
            
            widget.resize_window()
            return False
        
        self.connect("configure-event", configure_event)
        self.connect("draw", draw_event)
    
    def plot(self, cr):
        self.plot_bg.plot(cr)
        for plot in self.plots:
            plot.plot(cr)
    
    def resize_window(self):
        self.plot_bg.resize(self.width, self.height)
        self.plot_bg.draw()
        
        for plot in self.plots:
            plot.resize(self.width, self.height)
            plot.draw()
    
    def add_plot(self, plot):
        plot.viewport = self.viewport
        self.plots.append(plot)

if __name__ == '__main__':
    viewport = Viewport(-10, 10, -10, 10)
    
    window = gtk.Window()
    window.set_default_size(400, 300)
    
    plot = PlotArea(viewport)
    
    window.add(plot)
    
    window.connect("delete-event", gtk.main_quit)
    
    func = FunctionPlot(gamma)
    plot.add_plot(func)
    
    func2 = FunctionPlot(sin)
    plot.add_plot(func2)
    
    #window.maximize()
    window.show_all()
    
    gtk.main()
