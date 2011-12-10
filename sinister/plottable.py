class Plottable(object):
    def __init__(self, viewport):
        self.viewport = viewport
        self.x_interval = (self.viewport.min_x, self.viewport.max_x)
        self.y_interval = (self.viewport.min_y, self.viewport.max_y)
        
        self.dimensions = None
        
        
        self.viewport.connect_object('update', Plottable.viewport_update, self)
    
    def viewport_update(self):
        x_interval = (self.viewport.min_x, self.viewport.max_x)
        y_interval = (self.viewport.min_y, self.viewport.max_y)
        
        if self.x_interval != x_interval or self.y_interval != y_interval:
            self.x_interval = x_interval
            self.y_interval = y_interval
    
    def resize(self, dimensions):
        if self.dimensions != dimensions:
            self.dimensions = dimensions
        
    def plot(self, cr):
        pass
    
    def plot_to_window(self, px=None, py=None):
        width, height = self.dimensions
        x, y = None, None
        
        if px is not None:
            min_x, max_x = self.x_interval
            x = (px - min_x) * width / (max_x - min_x)
        
        if py is not None:
            min_y, max_y = self.y_interval
            y = (py - max_y) * height / (min_y - max_y)
        
        return (x, y) if None not in (x, y) else x or y
    
    def window_to_plot(self, wx=None, wy=None):
        width, height = self.dimensions
        x, y = None, None
        
        if wx is not None:
            min_x, max_x = self.x_interval
            x = (max_x - min_x) * wx / width + min_x
        
        if wy is not None:
            min_y, max_y = self.y_interval
            y = (min_y - max_y) * wy / height + max_y
        
        return (x, y) if None not in (x, y) else x or y
