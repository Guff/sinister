from sinister.plottable import Plottable
from sinister.config import conf

from gi.repository import Gdk
import cairo

class FunctionPlot(Plottable):
    def __init__(self, viewport, func):
        super().__init__(viewport)
        
        self.func = func
        self.color = Gdk.RGBA()
        self.color.parse(conf.function_plot.color)
    
    def plot(self, cr):
        width, height = self.dimensions
        
        cr.save()
        cr.set_operator(cairo.OPERATOR_OVER)
        
        for window_x in range(width + 1):
            window_y = self(window_x)
            if window_y is None:
                continue
            
            if window_y < -2 * height or window_y > 2 * height:
                cr.new_sub_path()
            else:
                cr.line_to(window_x, window_y)
        
        cr.set_line_width(1.0)
        Gdk.cairo_set_source_rgba(cr, self.color)
        cr.stroke()
        
        cr.restore()
    
    def __call__(self, window_x):
        plot_x = self.window_to_plot(wx=window_x)
        try:
            plot_y = self.func(plot_x)
        except:
            return None
        else:
            window_y = self.plot_to_window(py=plot_y)
            return window_y

class PlotBg(Plottable):
    def __init__(self, viewport, ticks=(1.0, 1.0)):
        super().__init__(viewport)
        
        self.ticks = ticks
    
    def plot(self, cr):
        cr.save()
        self.draw_axes(cr)
        self.draw_ticks(cr)
        cr.restore()
    
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
        width, height = self.dimensions
        window_x_ticks = x_ticks * width / (max_x - min_x)
        window_y_ticks = y_ticks * height / (max_y - min_y)
        
        cr.set_line_width(8)
        cr.set_source_rgb(0, 0, 0)
        
        plot_x = min_x - (min_x % x_ticks)
        window_x, window_y = self.plot_to_window(plot_x, 0)
        cr.move_to(window_x, window_y)
        cr.line_to(width, window_y)
        
        cr.set_dash([1.0, window_x_ticks - 1], 0.5)
        cr.stroke()
        
        plot_y = max_y - (max_y % y_ticks)
        window_x, window_y = self.plot_to_window(0, plot_y)
        cr.move_to(window_x, window_y)
        cr.line_to(window_x, height)
        
        cr.set_dash([1.0, window_y_ticks - 1], 0.5)
        cr.stroke()
