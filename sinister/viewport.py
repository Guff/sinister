from gi.repository import GObject

class Viewport(GObject.Object):
    __gsignals__ = {
        'update': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }
    
    def __init__(self, min_x, max_x, min_y, max_y):
        super().__init__()
        
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y
    
    def update(self, value_dict):
        for name in value_dict:
            setattr(self, name, value_dict[name])
        
        self.emit('update')
    
    def translate(self, dx, dy):
        self.update({'min_x': self.min_x - dx,
                     'max_x': self.max_x - dx,
                     'min_y': self.min_y + dy,
                     'max_y': self.max_y + dy
                    })
    
    def __iter__(self):
        return iter([self.min_x, self.max_x, self.min_y, self.max_y])

GObject.type_register(Viewport)
