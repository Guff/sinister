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
            if event.button != 1:
                return True
            
            allocation = widget.get_allocation()
            width, height = allocation.width, allocation.height
            x0, y0 = event.x, event.y
            
            min_x_0, max_x_0 = widget.viewport.min_x, widget.viewport.max_x
            min_y_0, max_y_0 = widget.viewport.min_y, widget.viewport.max_y
            
            viewport_width = max_x_0 - min_x_0
            viewport_height = max_y_0 - min_y_0
            
            x_ratio = viewport_width / width
            y_ratio = viewport_height / height
            
            def motion_notify(widget, event):
                dx = x_ratio * (event.x - x0)
                dy = y_ratio * (event.y - y0)
                widget.viewport.update({'min-x': min_x_0 - dx,
                                        'max-x': max_x_0 - dx,
                                        'min-y': min_y_0 + dy,
                                        'max-y': max_y_0 + dy
                                        })
            
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
        self.plot_bg.draw()
        
        for entry, plot in self.plots.items():
            plot.resize(self.dimensions)
            plot.draw()
    
    def update_plot(self, entry, plot):
        if plot is None:
            if entry in self.plots:
                del self.plots[entry]
        else:
            plot.resize(self.dimensions)
            plot.draw()
            
            self.plots[entry] = plot
    
    def refresh(self):
        self.queue_draw()
