class Viewport(object):
    def __init__(self, min_x, max_x, min_y, max_y, x_ticks, y_ticks):
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y
        self.x_ticks, self.y_ticks = x_ticks, y_ticks
