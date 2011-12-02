from gi.repository import GObject

class Viewport(GObject.GObject):
    __gsignals__ = {
        'update': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }
    
    min_x = GObject.property(type=float)
    max_x = GObject.property(type=float)
    min_y = GObject.property(type=float)
    max_y = GObject.property(type=float)
    
    def __init__(self, min_x, max_x, min_y, max_y):
        super().__init__()
        
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y
    
    def update(self, value_dict):
        for name in value_dict:
            self.set_property(name, value_dict[name])
        
        self.emit('update')
    
    def __iter__(self):
        return iter([self.min_x, self.max_x, self.min_y, self.max_y])

GObject.type_register(Viewport)
