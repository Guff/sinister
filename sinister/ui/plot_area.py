from sinister.plotters import PlotBg
from gi.repository import Gtk, Gdk

class PlotArea(Gtk.DrawingArea):
    def __init__(self, viewport, plot_bg):
        super().__init__()
        
        self.viewport = viewport
        self.plot_bg = plot_bg
        
        self.dimensions = None
        
        self.plots = {}
        
        self.set_can_focus(True)
        self.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK
                      | Gdk.EventMask.BUTTON_PRESS_MASK
                      | Gdk.EventMask.BUTTON_RELEASE_MASK
                      | Gdk.EventMask.POINTER_MOTION_MASK
                      | Gdk.EventMask.POINTER_MOTION_HINT_MASK
                      | Gdk.EventMask.KEY_PRESS_MASK
                      | Gdk.EventMask.KEY_RELEASE_MASK
                      | Gdk.EventMask.SCROLL_MASK)
        
        self.connect('configure-event', PlotArea.configure_event)
        self.connect('draw', PlotArea.draw_event)
        # make sure the plots et al. have all handled the viewport update
        # before we redraw
        self.viewport.connect_object_after('update', PlotArea.refresh, self)
        self.connect('button-press-event', PlotArea.button_2_press)
        self.connect('button-press-event', PlotArea.button_press)
    
    def draw_event(self, cr):
        self.plot(cr)
        return False
    
    def plot(self, cr):
        self.plot_bg.plot(cr)
        for entry, plot in self.plots.items():
            if entry.enabled:
                plot.plot(cr)
        
    def button_press(self, event):
        if event.button != 1 or event.type != Gdk.EventType.BUTTON_PRESS:
            return False
        
        self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND1))
        
        allocation = self.get_allocation()
        width, height = allocation.width, allocation.height
        prev_coords = {'x': event.x, 'y': event.y}
        
        viewport_width = self.viewport.max_x - self.viewport.min_x
        viewport_height = self.viewport.max_y - self.viewport.min_y
        
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
                widget.get_window().set_cursor(None)
                widget.handler_disconnect(handles['motion'])
                widget.handler_disconnect(handles['release'])
                return True
            else:
                return False
        
        # passing a mutable container (a dict in this case), which is then
        # updated to hold the handle IDs, to the release handler was the best
        # way i could think of to be able to disconnect the handles
        handles = {}
        
        handles['release'] = self.connect('button-release-event', button_release, handles)
        handles['motion'] = self.connect('motion-notify-event', motion_notify)
    
    def button_2_press(self, event):
        if event.button != 1 or event.type != Gdk.EventType._2BUTTON_PRESS:
            return False
        
        min_x0, max_x0, min_y0, max_y0 = self.viewport
        plot_width = max_x0 - min_x0
        plot_height = max_y0 - min_y0
        
        plot_x, plot_y = self.plot_bg.window_to_plot(event.x, event.y)
        plot_x = min(max(plot_x, min_x0 + plot_width / 4), max_x0 - plot_width / 4)
        plot_y = min(max(plot_y, min_y0 + plot_height / 4), max_y0 - plot_height / 4)
        
        new_limits = {'min_x': plot_x - plot_width / 4,
                      'max_x': plot_x + plot_width / 4,
                      'min_y': plot_y - plot_height / 4,
                      'max_y': plot_y + plot_height / 4}
        
        self.viewport.update(new_limits)
        
        return True
    
    def configure_event(self, event):
        if self.dimensions == (event.width, event.height):
            return True
        
        self.dimensions = (event.width, event.height)
        
        self.resize_window()
        
        return False
    
    def resize_window(self):
        self.plot_bg.resize(self.dimensions)
        
        for plot in self.plots.values():
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
