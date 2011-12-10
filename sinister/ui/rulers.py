from gi.repository import Gdk, Gtk

class Ruler(Gtk.Widget, Gtk.Orientable):
    def __init__(self, size=14):
        super().__init__()
        
        self.size = size
        self._position = 0.0
        
        sc = self.get_style_context()
        
        sc.add_class('frame')
    
    def get_position(self):
        return self._position
    
    def set_position(self, position):
        self._position = position
        self.queue_draw()
    
    def do_get_preferred_height(self):
        if self.orientation == Gtk.Orientation.HORIZONTAL:
            return (self.size, self.size)
        else:
            return super().do_get_preferred_height()
    
    def do_get_preferred_width(self):
        if self.orientation == Gtk.Orientation.HORIZONTAL:
            return super().do_get_preferred_width()
        else:
            return (self.size, self.size)
    
    def do_draw(self, cr):
        self.draw_rule(cr)
        self.draw_pos(cr)
        
        return False
    
    def draw_rule(self, cr):
        cr.save()
        
        horizontal = self.orientation == Gtk.Orientation.HORIZONTAL
        
        sc = self.get_style_context()
        alloc = self.get_allocation()
        
        orient, subdivs = self.orientation, self.subdivisions
        
        ruler_fg = sc.get_color(Gtk.StateFlags.NORMAL)
        Gdk.cairo_set_source_rgba(cr, ruler_fg)
        
        cr.set_line_width(1.0)
        
        if horizontal:
            span = alloc.width
        else:
            span = alloc.height
        
        # prevents a bit of code duplication
        flip_if_vertical = lambda x, y: (x, y) if horizontal else (y, x)
        
        for tick in range(0, span + 1, self.major_ticks_spacing):
            tick_start = flip_if_vertical(tick + 0.5, self.size)
            tick_end = flip_if_vertical(0, -(7 * self.size) // 9 - 0.5)
            
            cr.move_to(*tick_start)
            cr.rel_line_to(*tick_end)
            
            for subtick in range(1, subdivs):
                spacing = (subtick * self.major_ticks_spacing) // subdivs
                
                if subdivs % 2 == 0 and subtick == subdivs // 2:
                    subtick_size = self.size // 2
                else:
                    subtick_size = self.size // 4
                
                subtick_start = flip_if_vertical(tick + spacing + 0.5, self.size)
                subtick_end = flip_if_vertical(0, -subtick_size - 0.5)
                
                cr.move_to(*subtick_start)
                cr.rel_line_to(*subtick_end)
            
        cr.stroke()
        
        end = alloc.width if horizontal else alloc.height
        coords_start = flip_if_vertical(0, self.size - 1)
        coords_end = flip_if_vertical(end, self.size - 1)
        
        Gtk.render_line(sc, cr, *(coords_start + coords_end))
        
        cr.restore()
    
    def draw_pos(self, cr):
        cr.save()
        
        sc = self.get_style_context()
        
        horizontal = self.orientation == Gtk.Orientation.HORIZONTAL
        
        x, y = self.position - self.size // 4, self.size // 2 - 2
        x, y = (x, y) if horizontal else (y, x)
        Gtk.render_arrow(sc,
                         cr,
                         pi if horizontal else pi / 2,
                         x,
                         y,
                        # we need to ensure the arrow size is even,
                        # so it doesn't get blurrified
                         (self.size + (-self.size % 4)) // 2)
                
        cr.restore()
    
    def do_realize(self):
        self.set_realized(True)
        
        alloc = self.get_allocation()
        
        attr_mask = Gdk.WindowAttributesType.X
        attr_mask |= Gdk.WindowAttributesType.Y
        attr_mask |= Gdk.WindowAttributesType.VISUAL
        
        attrs = Gdk.WindowAttr()
        attrs.window_type = Gdk.WindowType.CHILD
        attrs.x, attrs.y = alloc.x, alloc.y
        attrs.width, attrs.height = alloc.width, alloc.height
        attrs.wclass = Gdk.WindowWindowClass.OUTPUT
        attrs.visual = self.get_visual()
        attrs.event_mask = self.get_events()
        attrs.event_mask |= Gdk.EventMask.EXPOSURE_MASK
        attrs.event_mask |= Gdk.EventMask.POINTER_MOTION_MASK
        attrs.event_mask |= Gdk.EventMask.POINTER_MOTION_HINT_MASK
        
        window = Gdk.Window(self.get_parent_window(), attrs, attr_mask)
        window.set_user_data(self)
        self.set_window(window)
        
        sc = self.get_style_context()
        sc.set_background(window)
    
    def do_motion_notify_event(self, event):
        if self.orientation == Gtk.Orientation.HORIZONTAL:
            self.position = event.x
        else:
            self.position = event.y
        
        if event.is_hint:
            event.request_motions()
    
    orientation = GObject.property(type=Gtk.Orientation, default=Gtk.Orientation.HORIZONTAL)
    position = GObject.property(type=float, getter=get_position, setter=set_position)
    size = GObject.property(type=int)
    major_ticks_spacing = GObject.property(type=int, default=100)
    subdivisions = GObject.property(type=int, default=10)

GObject.type_register(Ruler)

class HRuler(Ruler):
    def __init__(self, size=None):
        if size is not None:
            super().__init__(size)
        else:
            super().__init__()
        
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

GObject.type_register(HRuler)

class VRuler(Ruler):
    def __init__(self, size=None):
        if size is not None:
            super().__init__(size)
        else:
            super().__init__()
        
        self.set_orientation(Gtk.Orientation.VERTICAL)

GObject.type_register(VRuler)
