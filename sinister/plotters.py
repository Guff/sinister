from sinister.plottable import Plottable

import cairo

class FunctionPlot(Plottable):
    def __init__(self, viewport, func):
        super().__init__(viewport)
        
        self.func = func
    
    def draw(self):
        width, height = self.dimensions
        
        cr = cairo.Context(self.surface)
        cr.set_line_width(1.0)
        
        for window_x in range(width + 1):
            window_y = self(window_x)
            if window_y is None:
                continue
            
            cr.line_to(window_x, window_y)
        
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()
    
    def __call__(self, window_x):
        plot_x, _ = self.window_to_plot(window_x, 0)
        try:
            plot_y = self.func(plot_x)
        except:
            return None
        else:
            _, window_y = self.plot_to_window(0, plot_y)
            return window_y

class PlotBg(Plottable):
    def __init__(self, viewport, ticks=(1, 1)):
        super().__init__(viewport)
        
        self.ticks = ticks
    
    def draw(self):
        cr = cairo.Context(self.surface)
        self.draw_axes(cr)
        self.draw_ticks(cr)
    
    def draw_axes(self, cr):
        width, height = self.dimensions
        origin_x, origin_y = self.plot_to_window(0, 0)
        
        cr.set_source_rgb(1, 1, 1)
        cr.paint()
        
        cr.move_to(0, origin_y)
        cr.line_to(width, origin_y)
        
        cr.move_to(origin_x, 0)
        cr.line_to(origin_x, height)
        
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()
    
    def draw_ticks(self, cr):
        min_x, max_x = self.x_interval
        min_y, max_y = self.y_interval
        x_ticks, y_ticks = self.ticks
        
        plot_x = min_x - (min_x % x_ticks)
        while plot_x <= max_x:
            window_x, window_y = self.plot_to_window(plot_x, 0)
            cr.move_to(window_x, window_y - 4)
            cr.line_to(window_x, window_y + 4)
            plot_x += x_ticks
        
        plot_y = min_y - (min_y % y_ticks)
        while plot_y <= max_y:
            window_x, window_y = self.plot_to_window(0, plot_y)
            cr.move_to(window_x - 4, window_y)
            cr.line_to(window_x + 4, window_y)
            plot_y += y_ticks
        
        cr.set_line_width(1)
        cr.stroke()

