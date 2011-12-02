from sinister.plotters import PlotBg
from gi.repository import Gtk, Gdk

class PlotArea(Gtk.DrawingArea):
    def __init__(self, viewport, plot_bg):
        super().__init__()
        
        self.viewport = viewport
        self.plot_bg = plot_bg
        
        self.dimensions = None
        
        self.plots = {}
        
        def draw_event(widget, cr):
            widget.plot(cr)
            
            return False
        
        def configure_event(widget, event):
            if widget.dimensions == (event.width, event.height):
                return True
            
            widget.dimensions = (event.width, event.height)
            
            widget.resize_window()
            
            return False
        
        def viewport_update(viewport_obj):
            self.refresh()
        
        def button_press(widget, event):
            if event.button != 1 or event.type != Gdk.EventType.BUTTON_PRESS:
                return False
            
            allocation = widget.get_allocation()
            width, height = allocation.width, allocation.height
            prev_coords = {'x': event.x, 'y': event.y}
            
            viewport_width = widget.viewport.max_x - widget.viewport.min_x
            viewport_height = widget.viewport.max_y - widget.viewport.min_y
            
            x_ratio = viewport_width / width
            y_ratio = viewport_height / height
            
            def motion_notify(widget, event):
                x, y = event.x, event.y
                dx = x_ratio * (x - prev_coords['x'])
                dy = y_ratio * (y - prev_coords['y'])
                widget.viewport.translate(dx, dy)
                
                prev_coords['x'] = x
                prev_coords['y'] = y
            
            def button_release(widget, event, handles):
                if event.button == 1:
                    widget.handler_disconnect(handles['motion'])
                    widget.handler_disconnect(handles['release'])
                    return True
                else:
                    return False
            
            handles = {}
            
            handles['release'] = widget.connect('button-release-event',
                                                button_release, handles)
            
            handles['motion'] = widget.connect('motion-notify-event', motion_notify)
        
        self.set_can_focus(True)
        self.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK
                      | Gdk.EventMask.BUTTON_PRESS_MASK
                      | Gdk.EventMask.BUTTON_RELEASE_MASK
                      | Gdk.EventMask.POINTER_MOTION_MASK
                      | Gdk.EventMask.POINTER_MOTION_HINT_MASK
                      | Gdk.EventMask.KEY_PRESS_MASK
                      | Gdk.EventMask.KEY_RELEASE_MASK
                      | Gdk.EventMask.SCROLL_MASK)
        
        self.connect('configure-event', configure_event)
        self.connect('draw', draw_event)
        self.viewport.connect_after('update', viewport_update)
        self.connect('button-press-event', button_press)
    
    def plot(self, cr):
        self.plot_bg.plot(cr)
        for entry, plot in self.plots.items():
            if entry.enabled:
                plot.plot(cr)
    
    def resize_window(self):
        self.plot_bg.resize(self.dimensions)
        
        for entry, plot in self.plots.items():
            plot.resize(self.dimensions)
    
    def update_plot(self, entry, plot):
        if plot is None:
            if entry in self.plots:
                del self.plots[entry]
        else:
            plot.resize(self.dimensions)
            
            self.plots[entry] = plot
    
    def refresh(self):
        self.queue_draw()
