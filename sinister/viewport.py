from gi.repository import GObject

class Viewport(GObject.Object):
    __gsignals__ = {
        'update': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (bool,)),
    }
    
    def __init__(self, min_x, max_x, min_y, max_y):
        super().__init__()
        
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y
    
    def update(self, values, record=True):
        try:
            items = values.items()
        except AttributeError:
            self.min_x, self.max_x, self.min_y, self.max_y = values
        else:
            for name, value in items:
                setattr(self, name, value)
        
        self.emit('update', record)
    
    def translate(self, dx, dy, record=True):
        self.update((self.min_x - dx, self.max_x - dx,
                     self.min_y + dy,
                     self.max_y + dy),
                     record=record)
    
    def __iter__(self):
        return iter([self.min_x, self.max_x, self.min_y, self.max_y])

GObject.type_register(Viewport)
