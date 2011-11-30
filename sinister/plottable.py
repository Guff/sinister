import cairo

class Plottable(object):
    def __init__(self, viewport):
        self.viewport = viewport
        self.x_interval = (self.viewport.min_x, self.viewport.max_x)
        self.y_interval = (self.viewport.min_y, self.viewport.max_y)
        
        self.dimensions = None
        
        self.surface = None
        
        def viewport_update(viewport_obj, param_spec):
            x_interval = (viewport_obj.min_x, viewport_obj.max_x)
            y_interval = (viewport_obj.min_y, viewport_obj.max_y)
            
            if self.x_interval != x_interval or self.y_interval != y_interval:
                self.x_interval = x_interval
                self.y_interval = y_interval
                self.draw()
        
        self.viewport.connect('notify::min-x', viewport_update)
        self.viewport.connect('notify::max-x', viewport_update)
        self.viewport.connect('notify::min-y', viewport_update)
        self.viewport.connect('notify::max-y', viewport_update)
    
    def draw(self):
        pass
    
    def resize(self, dimensions):
        if self.dimensions != dimensions:
            self.dimensions = dimensions
        
            if self.surface is not None:
                self.surface.finish()
            
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self.dimensions)
    
    def plot(self, cr):
        cr.set_source_surface(self.surface)
        cr.paint()
    
    def plot_to_window(self, plot_x, plot_y):
        min_x, max_x = self.x_interval
        min_y, max_y = self.y_interval
        width, height = self.dimensions
        
        window_x = (plot_x - min_x) * width / (max_x - min_x)
        window_y = (plot_y - max_y) * height / (min_y - max_y)
        
        return (window_x, window_y)
    
    def window_to_plot(self, window_x, window_y):
        min_x, max_x = self.x_interval
        min_y, max_y = self.y_interval
        width, height = self.dimensions
        
        plot_x = (max_x - min_x) * window_x / width + min_x
        plot_y = (min_y - max_y) * window_y / height + max_y
        
        return (plot_x, plot_y)
