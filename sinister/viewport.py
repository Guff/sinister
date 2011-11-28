from gi.repository import GObject

class Viewport(GObject.Object):
    min_x = GObject.property(type=float)
    max_x = GObject.property(type=float)
    min_y = GObject.property(type=float)
    max_y = GObject.property(type=float)
    x_ticks = GObject.property(type=float, minimum=0)
    y_ticks = GObject.property(type=float, minimum=0)
    
    def __init__(self, min_x, max_x, min_y, max_y, x_ticks, y_ticks):
        super().__init__()
        
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y
        self.x_ticks, self.y_ticks = x_ticks, y_ticks

GObject.type_register(Viewport)
