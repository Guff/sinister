from sinister.plottable import Plottable

import cairo

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
    
    def __call__(self, window_x):
        plot_x, _ = self.window_to_plot(window_x, 0)
        try:
            plot_y = self.func(plot_x)
            _, y = self.plot_to_window(0, plot_y)
            return y
        except:
            return None

class PlotBg(Plottable):
    def draw(self):
        origin_x, origin_y = self.plot_to_window(0, 0)
        
        cr = cairo.Context(self.surface)
        
        cr.set_source_rgb(1, 1, 1)
        cr.paint()
        
        cr.move_to(0, origin_y)
        cr.line_to(self.width, origin_y)
        
        cr.move_to(origin_x, 0)
        cr.line_to(origin_x, self.height)
        
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()
        
        self.draw_ticks(cr)
    
    def draw_ticks(self, cr):
        min_x, max_x = self.viewport.min_x, self.viewport.max_x
        min_y, max_y = self.viewport.min_y, self.viewport.max_y
        x_ticks = self.viewport.x_ticks
        y_ticks = self.viewport.y_ticks
        
        x = min_x - (min_x % x_ticks)
        while x <= max_x:
            window_x, window_y = self.plot_to_window(x, 0)
            cr.move_to(window_x, window_y - 4)
            cr.line_to(window_x, window_y + 4)
            x += x_ticks
        
        y = min_y - (min_y % y_ticks)
        while y <= max_y:
            window_x, window_y = self.plot_to_window(0, y)
            cr.move_to(window_x - 4, window_y)
            cr.line_to(window_x + 4, window_y)
            y += y_ticks
        
        cr.set_line_width(1)
        cr.stroke()

