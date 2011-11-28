import cairo

class Plottable(object):
    def __init__(self):
        self.viewport = None
        self.width, self.height = None, None      
        
        self.active = True
        self.surface = None
    
    def toggle_active(self):
        self.active = not self.active
    
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
        if not self.active:
            return
        
        cr.set_source_surface(self.surface)
        cr.paint()
    
    def plot_to_window(self, px, py):
        min_x, max_x = self.viewport.min_x, self.viewport.max_x
        min_y, max_y = self.viewport.min_y, self.viewport.max_y
        width, height = self.width, self.height
        
        wx = (px - min_x) * width / (max_x - min_x)
        wy = (py - max_y) * height / (min_y - max_y)
        
        return (wx, wy)
    
    def window_to_plot(self, wx, wy):
        min_x, max_x = self.viewport.min_x, self.viewport.max_x
        min_y, max_y = self.viewport.min_y, self.viewport.max_y
        width, height = self.width, self.height
        
        px = (max_x - min_x) * wx / width + min_x
        py = (min_y - max_y) * wy / height + max_y
        
        return (px, py)
